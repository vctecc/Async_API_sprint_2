from aioredis import Redis
from typing import Optional, ClassVar, List

from pydantic import BaseModel
import orjson

from db.cache import Cache

redis: Redis = None


class RedisCache(Cache):
    def __init__(self):
        super().__init__()

    @property
    def client(self) -> Redis:
        return redis

    async def get(self, key: str) -> Optional[list]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: int):
        await self.client.set(key, value, expire=expire)
