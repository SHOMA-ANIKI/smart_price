from sqlalchemy import update
from src.core.models import User
from src.infrastructure.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(User, session)

    async def update_user(self, user_id: int, **kwargs) -> User | None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**kwargs)
            .returning(User)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
