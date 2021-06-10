from functools import lru_cache
from typing import Optional, List, Tuple

from fastapi import Depends
import orjson
from elasticsearch_dsl import Search, Q

from core.config import GENRE_CACHE_EXPIRE, GENRE_POPULARITY_CACHE_EXPIRE, GENRES_INDEX, FILM_WORKS_INDEX
from db.current_cache import get_current_cache
from db.current_storage import get_current_storage
from db.cache import Cache
from db.storage import Storage
from models.genre import Genre
from models.film import Film


class GenreService:
    prefix = "genres"

    def __init__(self, cache: Cache, storage: Storage, film_storage: Storage,
                 cache_expire: int, genre_popularity_cache_expire: int):
        self.cache = cache
        self.storage = storage
        self.film_storage = film_storage
        self.cache_expire = cache_expire
        self.genre_popularity_cache_expire = genre_popularity_cache_expire

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша.
        genre = await self._get_genre_from_cache(genre_id)
        if not genre:
            # Если жанра нет в кэше, то ищем его в хранилище.
            genre = await self._get_genre_from_storage(genre_id)
            if not genre:
                # Если он отсутствует в хранилище, значит, жанра вообще нет в базе.
                return None
            # Сохраняем жанр в кеш.
            await self._put_genre_to_cache(genre)
        return genre

    async def get_by_search(self,
                            query: str = None,
                            page: int = 1,
                            size: int = 10,
                            sort: str = None,
                            ) -> List[Genre]:

        params = (query, page, size, sort)
        genres = await self._get_genres_from_cache(str(params))

        if not genres:
            genres = await self._get_genres_from_storage(params)
            if not genres:
                return []

            data = orjson.dumps([f.dict() for f in genres], default=str)
            await self._put_genres_to_cache(str(params), data)
        return genres

    async def get_genre_popularity(self, genre_id: str) -> int:
        popularity = await self._get_genre_popularity_from_cache(genre_id)
        if not popularity:
            popularity = await self._get_genre_popularity_from_storage(genre_id)
            await self._put_genre_popularity_to_cache(str(genre_id), popularity)
        return popularity

    async def _get_genre_from_storage(self, genre_id: str) -> Optional[Genre]:
        return await self.storage.get(genre_id)

    async def _get_genres_from_storage(self, params: Tuple) -> List[Genre]:
        search = GenreService._create_query_search(*params)
        return await self.storage.search(search)

    async def _get_genre_popularity_from_storage(self, genre_id: str) -> int:
        s = Search()
        s = s.query(Q("nested", path="genres", query=Q("match", genres__id=genre_id)))
        return await self.film_storage.count(s.to_dict())

    async def _get_genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша.
        key = f"{self.prefix}:{genre_id}"
        return await self.cache.get(key)

    async def _get_genres_from_cache(self, params: str) -> Optional[Genre]:
        key = f"{self.prefix}:{params}"
        return await self.cache.get_query(key)

    async def _get_genre_popularity_from_cache(self, genre_id: str) -> int:
        key = f"{self.prefix}:popularity:{genre_id}"
        return await self.cache.get_custom_data(key)

    async def _put_genre_to_cache(self, genre: Genre):
        # Сохраняем данные в кэш.
        # Выставляем время жизни кеша.
        # pydantic позволяет сериализовать модель в json.
        key = f"{self.prefix}:{genre.id}"
        await self.cache.set(key, genre.json(), self.cache_expire)

    async def _put_genres_to_cache(self, params: str, genres):
        key = f"{self.prefix}:{params}"
        await self.cache.set(key, genres, self.cache_expire)

    async def _put_genre_popularity_to_cache(self, genre_id: str, popularity: int):
        key = f"{self.prefix}:popularity:{genre_id}"
        await self.cache.set(key, str(popularity), self.genre_popularity_cache_expire)

    @staticmethod
    def _create_query_search(query: str = None,
                             page: int = 1,
                             size: int = 10,
                             sort: str = None) -> dict:
        s = Search()
        if query:
            multi_match_fields = (
                "name^2", "description^1",
            )
            s = s.query("multi_match", query=query, fields=multi_match_fields)
        if sort:
            s = s.sort(sort)
        start = (page - 1) * size
        return s[start: start + size].to_dict()


@lru_cache()
def get_genre_service(
        cache: Cache = Depends(get_current_cache(model=Genre)),
        storage: Storage = Depends(get_current_storage(model=Genre, index=GENRES_INDEX)),
        films_storage: Storage = Depends(get_current_storage(model=Film, index=FILM_WORKS_INDEX))
) -> GenreService:
    return GenreService(cache, storage, films_storage, GENRE_CACHE_EXPIRE, GENRE_POPULARITY_CACHE_EXPIRE)
