import asyncio
import redis
from celery import Celery
from src.config import settings
from src.utils.unit_of_work import UnitOfWork
from src.utils.parser import get_wb_price
from src.utils.telegram import send_telegram_message

celery_app = Celery(
    "worker",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL
)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@celery_app.task(name="fetch_product_price")
def fetch_product_price(product_id: int):
    async def logic():
        async with UnitOfWork() as uow:
            product = await uow.products.find_one_or_none(id=product_id)
            if not product or not product.url:
                return

            new_price = await get_wb_price(product.url)
            if new_price is None:
                return

            old_price = product.price
            await uow.products.update_price(product.id, new_price)
            redis_client.set(f"product_price:{product.id}", new_price, ex=600)

            stmt = await uow.session.execute(
                uow.subs.model.__table__.select().where(
                    uow.subs.model.product_id == product.id
                )
            )
            subscriptions = stmt.fetchall()

            for sub in subscriptions:
                if new_price <= sub.target_price:
                    user = await uow.users.find_one_or_none(id=sub.user_id)
                    if user and user.tg_chat_id:
                        msg = (
                            f"<b>Цена упала!</b>\n"
                            f"Товар: {product.url}\n"
                            f"Новая цена: <b>{new_price} руб.</b>\n"
                            f"Ваша цель: {sub.target_price} руб."
                        )
                        await send_telegram_message(user.tg_chat_id, msg)

    asyncio.run(logic())

@celery_app.task(name="check_all_products")
def check_all_products():
    async def logic():
        async with UnitOfWork() as uow:
            products = await uow.products.get_all()
            for product in products:
                fetch_product_price.delay(product.id)
    asyncio.run(logic())

celery_app.conf.beat_schedule = {
    "refresh-prices-every-10-min": {
        "task": "check_all_products",
        "schedule": 600.0,
    },
}
