from functools import lru_cache
from typing import Optional, List

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search, Q

from fastapi import Depends

from db.elastic import AsyncElasticsearchStorage
from db.redis import RedisCache
from models.film import Film, FilmPreview
from core.config import FILM_CACHE_EXPIRE_IN_SECONDS


def create_query_search(query: str = None,
                        page: int = 1,
                        size: int = 10,
                        sort: str = None,
                        genre: str = None) -> dict:
    s = Search()
    if query:
        multi_match_fields = (
            'title^4', 'actors_names^3',
            'description^2', 'genres^2',
            'writers_names', 'directors_names',
        )
        s = s.query('multi_match', query=query, fields=multi_match_fields)
    if genre:
        s = s.query('nested', path='genres', query=Q('bool', filter=Q('term', genres__id=genre)))
    if sort:
        s = s.sort(sort)

    start = (page - 1) * size
    return s[start: start + size].to_dict()


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

    async def get_by_search(self,
                            query: str = None,
                            page: int = 1,
                            size: int = 10,
                            sort: str = None,
                            genre: str = None
                            ) -> List[FilmPreview]:

        params = (query, page, size, sort, genre)
        # films = await self.cache.get(self.prefix + str(params))
        # # TODO do it simply
        # if films:
        #     films = [FilmPreview(**item) for item in orjson.loads(films)]
        films = None
        if not films:
            search = create_query_search(*params)
            films = await self.storage.search(search)
            if not films:
                return []

            # data = orjson.dumps([f.dict() for f in films], default=str)
            # await self.cache.set(self.prefix + str(params), data, self.cache_expire)
        return films


@lru_cache()
def get_film_service(
        cache: Redis = Depends(RedisCache(Film)),
        storage: AsyncElasticsearch = Depends(AsyncElasticsearchStorage(Film, 'movies')),
) -> FilmService:
    return FilmService(cache, storage, FILM_CACHE_EXPIRE_IN_SECONDS)