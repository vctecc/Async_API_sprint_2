from typing import Optional, List, ClassVar

import orjson

from db.cache import Cache
from models.basic import AbstractModel


class BaseService:
    model: ClassVar
    cache: Cache

    async def get_record_from_cache(self, key: str) -> Optional[list]:
        data = await self.cache.get(key)
        if not data:
            return None

        return self.model.parse_raw(data)

    async def get_records_from_cache(self, query: str) -> Optional[List[AbstractModel]]:
        data = await self.cache.get(query)
        if not data:
            return None

        return [self.model(**item) for item in orjson.loads(data)]

    async def get_custom_data_from_cache(self, key: str):
        return await self.cache.get(key)

    async def save_to_cache(self, key: str, value: str, expire: int):
        await self.cache.set(key, value, expire=expire)

