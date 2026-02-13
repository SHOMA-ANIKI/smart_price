
from src.models import Subscription
from src.repositories.base import BaseRepository

class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session):
        super().__init__(Subscription, session)
