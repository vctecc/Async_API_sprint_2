from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from core.config import FILM_PAGE_SIZE, FILM_PAGE_NUMBER
from models.film import Film, FilmPreview
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get("/{film_id}", response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return film


@router.get("/", response_model=List[FilmPreview])
async def films_index(
        sort: Optional[str] = None,
        size: Optional[int] = Query(FILM_PAGE_SIZE, alias="page[size]"),
        page: Optional[int] = Query(FILM_PAGE_NUMBER, alias="page[number]"),
        genre: Optional[str] = Query(None, alias="filter[genre]"),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmPreview]:
    return await film_service.get_by_search(page=page, size=size, genre=genre, sort=sort)


@router.get("/search/", response_model=List[FilmPreview])
async def films_index(
        query: Optional[str] = None,
        sort: Optional[str] = None,
        size: Optional[int] = Query(FILM_PAGE_SIZE, alias="page[size]"),
        page: Optional[int] = Query(FILM_PAGE_NUMBER, alias="page[number]"),
        genre: Optional[str] = Query(None, alias="filter[genre]"),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmPreview]:
    return await film_service.get_by_search(query=query, page=page, size=size, genre=genre, sort=sort)

