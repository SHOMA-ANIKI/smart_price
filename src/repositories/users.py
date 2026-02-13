
from src.models import User
from src.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(User, session)
