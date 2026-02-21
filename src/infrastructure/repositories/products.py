from sqlalchemy import update, select
from src.core.models import Product
from src.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(Product, session)

    async def update_price(self, product_id: int, new_price: float):
        stmt = update(Product).where(Product.id == product_id).values(price=new_price)
        await self.session.execute(stmt)

    async def get_all(self):
        stmt = select(Product)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_top_drops(self, limit: int = 10):
        stmt = select(Product).where(Product.price.is_not(None)).order_by(Product.price.asc()).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()
