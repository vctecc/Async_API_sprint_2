import socket
from typing import Optional

import backoff
from aioredis import Redis

from core.config import BACKOFF_FACTOR, CACHE_BACKOFF_TIME
from db.cache import Cache

redis: Redis = None


class RedisCache(Cache):
    def __init__(self):
        super().__init__()

    @property
    def client(self) -> Redis:
        return redis

    # aioredis misses high-level exceptions when loosing connection while using connection pool
    # instead of single connection. This is why we have to stick with socket.gaierror.
    @backoff.on_exception(backoff.expo,
                          socket.gaierror,
                          max_time=CACHE_BACKOFF_TIME,
                          factor=BACKOFF_FACTOR)
    async def get(self, key: str) -> Optional[list]:
        return await self.client.get(key)

    @backoff.on_exception(backoff.expo,
                          socket.gaierror,
                          max_time=CACHE_BACKOFF_TIME,
                          factor=BACKOFF_FACTOR)
    async def set(self, key: str, value: str, expire: int):
        await self.client.set(key, value, expire=expire)
