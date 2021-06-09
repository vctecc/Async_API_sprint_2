from functools import lru_cache
from typing import Optional, List

from db.cache import Cache
from db.storage import Storage

from fastapi import Depends

from core.config import GENRE_CACHE_EXPIRE
from db.current_cache import get_current_cache
from db.current_storage import get_current_storage
from models.genre import Genre


class GenreService:
    prefix = "genres"

    def __init__(self, cache: Cache, storage: Storage, cache_expire: int):
        self.cache = cache
        self.storage = storage
        self.cache_expire = cache_expire

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

    async def get_all(self) -> List[Genre]:
        pass

    async def get_genre_popularity(self, genre_id) -> int:
        pass

    async def _get_genre_from_storage(self, genre_id: str) -> Optional[Genre]:
        return await self.storage.get(genre_id)

    async def _get_genres_from_storage(self) -> List[Genre]:
        pass

    async def _get_genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша.
        key = f"{self.prefix}:{genre_id}"
        return await self.cache.get(key)

    async def _put_genre_to_cache(self, genre: Genre):
        # Сохраняем данные в кэш.
        # Выставляем время жизни кеша.
        # pydantic позволяет сериализовать модель в json.
        key = f"{self.prefix}:{genre.id}"
        await self.cache.set(key, genre.json(), self.cache_expire)


@lru_cache()
def get_genre_service(
        cache: Cache = Depends(get_current_cache(model=Genre)),
        storage: Storage = Depends(get_current_storage(model=Genre, index="genres")),
) -> GenreService:
    return GenreService(cache, storage, GENRE_CACHE_EXPIRE)
