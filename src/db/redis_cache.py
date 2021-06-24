import socket
from asyncio import TimeoutError
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

    # aioredis misses high-level exceptions for lost connections while using connection pool
    # instead of single connection. This is why we have to stick with low level `socket.gaierror`.
    # The error is raised after some implicit timeout if the address is not resolved.
    # Max timeout can be set explicitly for connection pool to decrease this implicit waiting time
    # (timeout kwarg in `create_redis_pool`). It triggers `aioredis.exceptions.TimeoutError` if
    # `open_connection` is not awaited (or raised error) within timeout limits.
    # It is not obvious, whichever exception will trigger first.
    @backoff.on_exception(backoff.expo,
                          (socket.gaierror, TimeoutError),
                          max_time=CACHE_BACKOFF_TIME,
                          factor=BACKOFF_FACTOR)
    async def get(self, key: str) -> Optional[list]:
        return await self.client.get(key)

    @backoff.on_exception(backoff.expo,
                          (socket.gaierror, TimeoutError),
                          max_time=CACHE_BACKOFF_TIME,
                          factor=BACKOFF_FACTOR)
    async def set(self, key: str, value: str, expire: int):
        await self.client.set(key, value, expire=expire)
