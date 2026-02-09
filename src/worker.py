import asyncio
import random
import redis
from celery import Celery
from sqlalchemy import update, select

from src.config import settings
from src.database import async_session_maker
from src.models import Product

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

celery_app = Celery(
    "worker",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL
)



async def update_product_price_logic(product_id: int):
    async with async_session_maker() as session:
        new_price = round(random.uniform(500, 5000), 2)

        stmt = update(Product).where(Product.id == product_id).values(price=new_price)
        await session.execute(stmt)
        await session.commit()


        redis_client.set(f"product_price:{product_id}", new_price, ex=600)

        return new_price



@celery_app.task
def fetch_product_price(product_id: int):
    price = asyncio.run(update_product_price_logic(product_id))
    return f"Product {product_id} updated. Price: {price}"



async def get_all_product_ids():
    async with async_session_maker() as session:
        stmt = select(Product.id)
        result = await session.execute(stmt)
        return result.scalars().all()


@celery_app.task
def check_all_prices():
    product_ids = asyncio.run(get_all_product_ids())
    for p_id in product_ids:
        fetch_product_price.delay(p_id)
    return f"Sent {len(product_ids)} products to update"



celery_app.conf.beat_schedule = {
    "refresh-prices-every-10-min": {
        "task": "src.worker.check_all_prices",
        "schedule": 600.0,
    },
}
