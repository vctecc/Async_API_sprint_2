from fastapi import APIRouter
from fastapi import Depends

from models.person import Person
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    return person
