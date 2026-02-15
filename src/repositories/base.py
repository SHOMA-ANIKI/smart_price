
from typing import TypeVar, Generic, Type, Optional, Sequence
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, obj_id: int) -> Optional[T]:
        stmt = select(self.model).filter_by(id=obj_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_one_or_none(self, **filter_by) -> Optional[T]:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, data: dict) -> T:
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()
