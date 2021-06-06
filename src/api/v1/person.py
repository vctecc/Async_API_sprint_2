from typing import List

from fastapi import APIRouter
from fastapi import Depends

from models.person import BasePerson, Person
from services.person import PersonService, get_person_service

PERSONS_PAGE_SIZE = 5

router = APIRouter()


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    return person


@router.get('/search/', response_model=List[Person])
async def person_search(query: str = "", page: int = 1, page_size: int = PERSONS_PAGE_SIZE,
                        person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    persons = await person_service.search(query, page, page_size)
    return persons
