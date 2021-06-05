from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import AsyncElasticsearchStorage
from db.redis import RedisCache
from models.film import Film
from core.config import FILM_CACHE_EXPIRE_IN_SECONDS


class FilmService:
    prefix = 'FilmService'

    def __init__(self, cache: Redis, storage: AsyncElasticsearch, cache_expire: int):
        self.cache = cache
        self.storage = storage
        self.cache_expire = cache_expire

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self.cache.get(film_id)
        if not film:
            film = await self.storage.get(film_id)
            if not film:
                return None
            await self.cache.set(film.id, film.json(), self.cache_expire)
        return film


@lru_cache()
def get_film_service(
        cache: Redis = Depends(RedisCache(Film)),
        storage: AsyncElasticsearch = Depends(AsyncElasticsearchStorage(Film, 'movies')),
) -> FilmService:
    return FilmService(cache, storage, FILM_CACHE_EXPIRE_IN_SECONDS)
