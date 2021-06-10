from functools import lru_cache
from typing import List, Optional

import orjson
from elasticsearch_dsl import Q, Search
from fastapi import Depends

from core.config import FILM_CACHE_EXPIRE, FILM_WORKS_INDEX, PERSONS_INDEX, PERSON_CACHE_EXPIRE
from db.cache import Cache
from db.current_cache import get_current_cache
from db.current_storage import get_current_storage
from db.storage import Storage
from models.film import Film, FilmPreview
from models.person import BasePerson, Person


def create_person_films_query(person_id: str, role: str) -> dict:
    """Create query for ElasticSearch to get films where person occupied given role"""
    s = Search()
    q = s.query(Q("nested", path=f"{role}s", query=Q("match", **{f"{role}s.id": person_id})))
    return q.to_dict()


def create_person_search_query(query: str,
                               page: int = 1,
                               page_size: int = 5) -> dict:
    """
    Create query for ElasticSearch to get persons by search string
    :param query: string to search in full names
    :param page: page number
    :param page_size: page size
    :return: dict with ES query params
    """
    s = Search()
    start = (page - 1) * page_size
    q = s.query("match", full_name=query)[start:start + page_size]
    query = q.to_dict()
    return query


def create_films_by_person_query(person_id):
    """
    Create query to get films of given person from ElasticSearch
    :param person_id:
    :return: dict
    """
    s = Search()
    q = s.query(Q("nested", path="actors", query=Q("match", actors__id=person_id))
                | Q("nested", path="writers", query=Q("match", writers__id=person_id))
                | Q("nested", path="directors", query=Q("match", directors__id=person_id))
                )
    return q.to_dict()


class PersonService:
    prefix = "person_search"

    def __init__(self, cache: Cache, storage: Storage, film_cache: Cache, film_storage: Storage):
        self.cache = cache
        self.storage = storage
        self.film_storage = film_storage
        self.film_cache = film_cache

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self.cache.get(f"{self.prefix}:{person_id}")
        if not person:
            person = await self._person_from_storage(person_id)
            if not person:
                return None
            await self.cache.set(f"{self.prefix}:{person.id}", person.json(), expire=PERSON_CACHE_EXPIRE)
        return person

    async def _person_from_storage(self, person_id: str) -> Optional[Person]:
        person = await self.storage.get(person_id)
        if not person:
            return None
        person = person.dict()
        person["films"] = await self._get_filmworks(person_id)
        return Person.parse_obj(person)

    async def _get_filmworks(self, person_id: str) -> Optional[List[dict]]:
        """
        Find films which given person did create
        :param person_id:
        :return: List[dict]
        """
        roles = ("writer", "director", "actor")
        all_films = []
        for role in roles:
            films = await self._get_filmworks_by_person_job(person_id, role)
            films = [{"id": film.id, "role": role} for film in films]
            all_films.extend(films)
        return all_films

    async def _get_filmworks_by_person_job(self, person_id: str, role: str) -> Optional[List[Film]]:
        query = create_person_films_query(person_id, role)
        films = await self.film_storage.search(query)
        return films or []

    async def search(self, query: str, page: int, page_size: int) -> Optional[List[Person]]:
        """
        Search persons by name
        :param query: query string to search in full names
        :param page: page number
        :param page_size: page size
        :return: paginated list of persons who match the query
        """
        query = create_person_search_query(query, page, page_size)
        persons = await self.cache.get_query(f"{self.prefix}:{query}")
        if not persons:
            persons = await self.storage.search(query)
            persons = [await self.get_by_id(p.id) for p in persons]  # get Person instances from BasePerson
            serialized_persons = orjson.dumps([p.dict() for p in persons], default=str)
            await self.cache.set(f"{self.prefix}:{query}", serialized_persons, PERSON_CACHE_EXPIRE)
        if not persons:
            return None
        return persons

    async def get_films_by_person(self, person_id: str) -> List[FilmPreview]:
        """
        Get preview for films of given person
        :param person_id: uuid of the person
        :return: List[FilmPreview] with films of person with given person_id
        """
        query = create_films_by_person_query(person_id)
        films = await self.film_cache.get_query(f"{self.prefix}:{query}")
        if not films:
            films = await self.film_storage.search(query)
            serialized_films = orjson.dumps([f.dict() for f in films], default=str)
            await self.film_cache.set(f"{self.prefix}:{query}", serialized_films, expire=FILM_CACHE_EXPIRE)
        films = [FilmPreview.parse_obj(film) for film in films]
        return films


@lru_cache()
def get_person_service(
        cache: Cache = Depends(get_current_cache(model=Person)),
        film_cache: Cache = Depends(get_current_cache(model=Film)),
        storage: Storage = Depends(get_current_storage(model=BasePerson, index=PERSONS_INDEX)),
        film_storage: Storage = Depends(get_current_storage(model=Film, index=FILM_WORKS_INDEX)),
) -> PersonService:
    return PersonService(cache, storage, film_cache, film_storage)
