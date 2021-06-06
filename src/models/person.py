from typing import List

from models.basic import AbstractModel


class BasePerson(AbstractModel):
    id: str
    full_name: str


class Person(BasePerson):
    actor_in: List[dict]
    creator_in: List[dict]
