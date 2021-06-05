from typing import List

from models.basic import AbstractModel


class BasePerson(AbstractModel):
    full_name: str


class Person(BasePerson):
    films_ids: List[str]
