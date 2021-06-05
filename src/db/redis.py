from aioredis import Redis
from typing import Optional, ClassVar

from db.cache import Cache
redis: Redis = None


class RedisCache(Cache):
    def __init__(self, model: ClassVar, ):
        super().__init__()
        self.model = model

    def __call__(self):
        return self

    @property
    def client(self) -> Redis:
        return redis

    async def get(self, key: str) -> Optional[list]:
        data = await self.client.get(key)
        if not data:
            return None
        return self.model.parse_raw(data)

    async def get_many(self, key: str) -> Optional[list]:
        pass

    async def set(self, key: str, value: str, expire: int):
        await self.client.set(key, value, expire=expire)
