import asyncio
from celery import Celery
from src.core.config import settings

# Импортируем наши новые адаптеры и UoW
from src.infrastructure.unit_of_work import UnitOfWork
from src.utils.parser import WBParser
from src.utils.telegram import TelegramNotifier
from src.infrastructure.redis import redis_cache

celery_app = Celery(
    "worker",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL
)

wb_parser = WBParser()
telegram = TelegramNotifier()


@celery_app.task(name="fetch_product_price")
def fetch_product_price(product_id: int):
    async def process():
        async with UnitOfWork() as uow:
            product = await uow.products.get_by_id(product_id)
            if not product or not product.url:
                return

            new_price = await wb_parser.get_price(product.url)
            if new_price is None:
                return

            await uow.products.update_price(product.id, new_price)
            await redis_cache.set(f"product_price:{product.id}", str(new_price), expire=600)

            subscriptions = await uow.subs.find_all(product_id=product.id)

            for sub in subscriptions:
                if new_price <= sub.target_price:
                    user = await uow.users.get_by_id(sub.user_id)
                    if user and user.tg_chat_id:
                        msg = (
                            f"📉 <b>Цена упала!</b>\n"
                            f"Товар: {product.url}\n"
                            f"Новая цена: <b>{new_price} ₽</b>\n"
                            f"Ваша цель: {sub.target_price} ₽"
                        )
                        await telegram.send_message(user.tg_chat_id, msg)

            await uow.commit()

    asyncio.run(process())


@celery_app.task(name="check_all_products")
def check_all_products():
    async def process():
        async with UnitOfWork() as uow:
            products = await uow.products.find_all()
            for product in products:
                fetch_product_price.delay(product.id)

    asyncio.run(process())


celery_app.conf.beat_schedule = {
    "refresh-prices-every-10-min": {
        "task": "check_all_products",
        "schedule": 600.0,
    },
}
