from aioredis import Redis
from typing import Optional, ClassVar, List

from pydantic import BaseModel
import orjson

from db.cache import Cache

redis: Redis = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis

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

    async def get_query(self, query: str) -> Optional[List[BaseModel]]:
        data = await self.client.get(query)
        if not data:
            return None

        return [self.model(**item) for item in orjson.loads(data)]

    async def get_many(self, key: str) -> Optional[list]:
        pass

    async def set(self, key: str, value: str, expire: int):
        await self.client.set(key, value, expire=expire)
