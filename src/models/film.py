from typing import List, Optional

from models.basic import AbstractModel
from models.person import BasePerson
from models.genre import Genre


class Film(AbstractModel):
    title: str
    imdb_rating: Optional[float]
    description: str
    actors_names: List[str]
    writers_names: List[str]
    directors_names: List[str]
    genres_names: List[str]
    actors: List[BasePerson]
    writers: List[BasePerson]
    directors: List[BasePerson]
    genres: List[Genre]


class FilmPreview(AbstractModel):
    title: str
    imdb_rating: Optional[float]
    description: str
