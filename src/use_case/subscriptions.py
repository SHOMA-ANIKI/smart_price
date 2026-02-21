from src.core.schemas import SubscriptionCreateSchema
from src.infrastructure.unit_of_work import IUnitOfWork
from src.worker import fetch_product_price

class SubscribeUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, user_id: int, sub_data: SubscriptionCreateSchema) -> int:
        async with self.uow:
            product = await self.uow.products.find_one_or_none(url=str(sub_data.url))
            if not product:
                product = await self.uow.products.add({"url": str(sub_data.url)})
                await self.uow.session.flush()

            await self.uow.subs.add({
                "user_id": user_id,
                "product_id": product.id,
                "target_price": sub_data.target_price
            })

            await self.uow.commit()
            fetch_product_price.delay(product.id)
            return product.id
