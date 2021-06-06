from functools import lru_cache
from pprint import pprint
from typing import List, Optional

import orjson
from fastapi import Depends

from db.cache import Cache
from db.storage import Storage
from db.storage_implementation import AsyncElasticsearchStorage
from db.cache_implementation import RedisCache
from models.film import Film
from models.person import BasePerson, Person

CACHE_EXPIRE = 1  # seconds


class PersonService:
    prefix = 'person_search'

    def __init__(self, cache: Cache, storage: Storage, film_storage: Storage):
        self.cache = cache
        self.storage = storage
        self.film_storage = film_storage

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self.cache.get(f"{self.prefix}:{person_id}")
        if not person:
            person = await self._person_from_storage(person_id)
            if not person:
                return None
            await self.cache.set(f"{self.prefix}:{person.id}", person.json(), expire=CACHE_EXPIRE)
        return person

    async def _person_from_storage(self, person_id: str) -> Optional[Person]:
        person = await self.storage.get(person_id)
        if not person:
            return None
        person = person.dict()
        person['films'] = await self._get_filmworks(person_id)
        return Person.parse_obj(person)

    async def _get_filmworks(self, person_id: str) -> Optional[List[dict]]:
        """
        Find films which given person did create
        :param person_id:
        :return: List[dict]
        """
        roles = ('writer', 'director', 'actor')
        all_films = []
        for role in roles:
            films = await self._get_filmworks_by_person_job(person_id, role)
            films = [{"id": film.id, "role": role} for film in films]
            all_films.extend(films)
        pprint(all_films)
        return all_films

    async def _get_filmworks_by_person_job(self, person_id: str, role: str) -> Optional[List[Film]]:
        query = {
            'query': {
                'nested': {
                    'path': f'{role}s',
                    'query': {
                        'match': {
                            f'{role}s.id': person_id
                        }
                    }
                }
            }
        }
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
        query = {
            'from': (page - 1) * page_size,
            'size': page_size,
            'query': {
                'match': {
                    'full_name': query
                }
            }
        }
        persons = await self.cache.get_query(f"{self.prefix}:{query}")
        if not persons:
            persons = await self.storage.search(query)
            persons = [await self.get_by_id(p.id) for p in persons]  # get Person instances from BasePerson
            serialized_persons = orjson.dumps([p.dict() for p in persons], default=str)
            await self.cache.set(f"{self.prefix}:{orjson.dumps(query)}", serialized_persons, CACHE_EXPIRE)
        if not persons:
            return None
        return persons


@lru_cache()
def get_person_service(
        cache: RedisCache = Depends(RedisCache(Person)),
        storage: AsyncElasticsearchStorage = Depends(AsyncElasticsearchStorage(BasePerson, 'persons')),
        film_storage: AsyncElasticsearchStorage = Depends(AsyncElasticsearchStorage(Film, 'movies')),
) -> PersonService:
    return PersonService(cache, storage, film_storage)
