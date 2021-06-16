from functools import lru_cache
from typing import Optional, List, ClassVar

import orjson
from elasticsearch_dsl import Search, Q
from fastapi import Depends

from core.config import FILM_CACHE_EXPIRE, FILM_WORKS_INDEX
from db.cache import Cache
from db.current_cache import get_current_cache
from db.current_storage import get_current_storage
from db.storage import Storage
from models.film import Film, FilmPreview
from services.basic import BaseService


def create_query_search(query: str = None,
                        page: int = 1,
                        size: int = 10,
                        sort: str = None,
                        genre: str = None) -> dict:
    s = Search()
    if query:
        multi_match_fields = (
            "title", "actors_names",
            "description", "genres_names",
            "writers_names", "directors_names",
        )
        s = s.query("multi_match", query=query, fields=multi_match_fields)
    if genre:
        s = s.query("nested", path="genres",
                    query=Q("bool", filter=Q("term", genres__id=genre)))
    if sort:
        s = s.sort(sort)

    start = (page - 1) * size
    return s[start: start + size].to_dict()


class FilmService(BaseService):
    prefix = "film_search"

    def __init__(self, model: ClassVar, cache: Cache, storage: Storage, cache_expire: int):
        self.model = model
        self.cache = cache
        self.storage = storage
        self.cache_expire = cache_expire

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        key = f"{self.prefix}:{film_id}"
        film = await self.get_record_from_cache(key)
        if not film:
            film = await self.storage.get(film_id)
            if not film:
                return None
            await self.save_to_cache(key, film.json(), self.cache_expire)
        return film

    async def get_by_search(self,
                            query: str = None,
                            page: int = 1,
                            size: int = 10,
                            sort: str = None,
                            genre: str = None
                            ) -> List[FilmPreview]:

        params = (query, page, size, sort, genre)
        key = f"{self.prefix}:{str(params)}"

        films = await self.get_records_from_cache(key)
        if not films:
            search = create_query_search(*params)
            films = await self.storage.search(search)
            if not films:
                return []

            data = orjson.dumps([f.dict() for f in films], default=str)
            await self.save_to_cache(key, data, self.cache_expire)
        return films


@lru_cache()
def get_film_service(
        cache: Cache = Depends(get_current_cache()),
        storage: Storage = Depends(get_current_storage(model=Film, index=FILM_WORKS_INDEX)),
) -> FilmService:
    return FilmService(Film, cache, storage, FILM_CACHE_EXPIRE)
