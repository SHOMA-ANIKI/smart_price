from sqlalchemy import update

from src.models import User
from src.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(User, session)

    async def update_user(self, user_id: int, **kwargs):
        stmt = update(User).where(User.id == user_id).values(**kwargs)
        await self.session.execute(stmt)