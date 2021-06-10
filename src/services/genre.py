from functools import lru_cache
from typing import Optional, List

from db.cache import Cache
from db.storage import Storage

from fastapi import Depends

from db.storage_implementation import get_storage
from db.cache_implementation import get_cache
from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 60  # 60 минут


class GenreService:
    def __init__(self, cache: Cache, storage: Storage):
        self.cache = cache
        self.storage = storage

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша.
        genre = await self._get_genre_from_cache(genre_id)
        if not genre:
            # Если жанра нет в кеше, то ищем его в хранилище.
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
        doc = await self.storage.get(model="genre", id=genre_id)
        return Genre(**doc["_source"])

    async def _get_genres_from_storage(self) -> List[Genre]:
        pass

    async def _get_genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша.
        data = await self.cache.get("genre: {genre.id}")
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json.
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        # Сохраняем данные в кэш.
        # Выставляем время жизни кеша.
        # pydantic позволяет сериализовать модель в json.
        await self.cache.set(f"genre: {genre.id}", genre.json(), expire=GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        cache: Cache = Depends(get_cache),
        storage: Storage = Depends(get_storage),
) -> GenreService:
    return GenreService(cache, storage)
