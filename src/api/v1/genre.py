from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str
    name: str
    popularity: int


@router.get("/{genre_id}", response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Genre not found")

    return Genre(id=genre.id, name=genre.name, popularity=10)


@router.get("/", response_model=List[Genre])
async def genre_index(
        query: str = None,
        sort: Optional[str] = None,
        size: Optional[int] = Query(25),
        page: Optional[int] = Query(1),
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    return [Genre(id=genre.id, name=genre.name, popularity=15) for genre in await genre_service.get_by_search(
        query=query, page=page, size=size, sort=sort)]
