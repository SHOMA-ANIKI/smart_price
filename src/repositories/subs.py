from sqlalchemy import select, update, delete
from src.models import Subscription
from src.repositories.base import BaseRepository

class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session):
        super().__init__(Subscription, session)

    async def delete_sub(self, user_id: int, product_id: int):
        stmt = delete(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.product_id == product_id
        )
        await self.session.execute(stmt)

    async def update_target_price(self, sub_id: int, user_id: int, new_price: float):
        stmt = (
            update(Subscription)
            .where(Subscription.id == sub_id, Subscription.user_id == user_id)
            .values(target_price=new_price)
            .returning(Subscription)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_subs(self, user_id: int):
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_all_user_subs(self, user_id: int):
        stmt = delete(Subscription).where(Subscription.user_id == user_id)
        await self.session.execute(stmt)

    async def get_user_stats(self, user_id: int):
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        res = await self.session.execute(stmt)
        subs = res.scalars().all()
        return {
            "total_subscriptions": len(subs),
            "active_items": len(set(s.product_id for s in subs))
        }
