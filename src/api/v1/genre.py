from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from services.genre import GenreService, get_genre_service
from core.config import GENRE_PAGE_SIZE, GENRE_PAGE_NUMBER

router = APIRouter()


class Genre(BaseModel):
    id: str = Field("Идентификатор")
    name: str = Field("Название")
    popularity: int = Field("Популярность: в скольких фильмах был указан жанр")


@router.get("/{genre_id}", response_model=Genre, description="Вывод жанра с указанным ID")
async def genre_details(genre_id: str = Query(None, description="Идентификатор"), genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return Genre(id=genre.id, name=genre.name, popularity=await genre_service.get_genre_popularity(genre.id))


@router.get("/", response_model=List[Genre], description="Вывод всех жанров.")
async def genre_index(
        size: Optional[int] = Query(GENRE_PAGE_SIZE, ge=1,
                                    description="Положительное число, указывающее размер страницы."),
        page: Optional[int] = Query(GENRE_PAGE_NUMBER, ge=1,
                                    description="Положительное число, указывающее номер страницы."),
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    return [Genre(id=genre.id, name=genre.name, popularity=await genre_service.get_genre_popularity(str(genre.id)))
            for genre in await genre_service.get_by_search(
        query=None, page=page, size=size, sort=None)]


@router.get("/search/", response_model=List[Genre], description="Поиск жанра.")
async def genre_search(
        query: str = Query("", description="Строка для поиска"),
        size: Optional[int] = Query(GENRE_PAGE_SIZE, ge=1,
                                    description="Положительное число, указывающее размер страницы."),
        page: Optional[int] = Query(GENRE_PAGE_NUMBER, ge=1,
                                    description="Положительное число, указывающее номер страницы."),
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    return [Genre(id=genre.id, name=genre.name, popularity=await genre_service.get_genre_popularity(str(genre.id)))
            for genre in await genre_service.get_by_search(
        query=query, page=page, size=size, sort=None)]
