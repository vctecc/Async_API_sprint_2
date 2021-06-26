from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from models.film import FilmPreview
from models.person import Person
from services.person import PersonService, get_person_service

PERSONS_PAGE_SIZE = 5

router = APIRouter()


@router.get("/{person_id}",
            response_model=Person,
            description="Подробная информация о участнике кинопроизведения с указанным ID.",
            )
async def person_details(person_id: str = Query(None, description="Идентификатор"),
                         person_service: PersonService = Depends(get_person_service)
                         ) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person


@router.get("/search/",
            response_model=List[Person],
            description="Поиск среди участников кинопроизведения.",
            )
async def person_search(query: str = Query("", description="Полнотекстовый поиск участникам."),
                        page: Optional[int] = Query(1, alias="page[number]", ge=1,
                                                    description="Порядковый номер страницы."),
                        page_size: Optional[int] = Query(PERSONS_PAGE_SIZE, alias="page[size]", ge=1,
                                                         description="Количество персон на запрашиваемой странице."),
                        person_service: PersonService = Depends(get_person_service)
                        ) -> List[Person]:
    persons = await person_service.search(query, page, page_size)
    return persons


@router.get("/{person_id}/film",
            response_model=List[FilmPreview],
            description="Краткая информация о фильмах, в которых приняла участие персона.",
            )
async def person_films(person_id: str,
                       person_service: PersonService = Depends(get_person_service)
                       ) -> List[FilmPreview]:
    films = await person_service.get_films_by_person(person_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return films
