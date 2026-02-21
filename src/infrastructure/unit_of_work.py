from src.database import async_session_maker
from src.repositories.users import UserRepository
from src.repositories.products import ProductRepository
from src.repositories.subs import SubscriptionRepository


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):

        self.session = self.session_factory()


        self.users = UserRepository(self.session)
        self.products = ProductRepository(self.session)
        self.subs = SubscriptionRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
