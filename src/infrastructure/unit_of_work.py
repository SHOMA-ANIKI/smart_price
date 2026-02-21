from abc import ABC, abstractmethod
from src.database import async_session_maker
from src.infrastructure.repositories.users import UserRepository
from src.infrastructure.repositories.products import ProductRepository
from src.infrastructure.repositories.subs import SubscriptionRepository


class IUnitOfWork(ABC):
    users: UserRepository
    products: ProductRepository
    subs: SubscriptionRepository

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork(IUnitOfWork):
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
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
