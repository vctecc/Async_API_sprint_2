from typing import List

from models.basic import AbstractModel


class BasePerson(AbstractModel):
    id: str
    full_name: str


class FilmRole(AbstractModel):
    id: str  # Film id
    role: str  # Person role in Film


class Person(BasePerson):
    films: List[FilmRole]
