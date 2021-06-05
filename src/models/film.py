from typing import List

from models.basic import AbstractModel
from models.person import BasePerson


class Film(AbstractModel):
    title: str
    description: str
    actors_names: List[str]
    writers_names: List[str]
    directors_names: List[str]
    genres_names: List[str]
    actors: List[BasePerson]
    writers: List[BasePerson]
    directors: List[BasePerson]
    genres: List[BasePerson]

