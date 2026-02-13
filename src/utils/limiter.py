
from slowapi import Limiter
from slowapi.util import get_remote_address
import os


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)


