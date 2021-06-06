import json
from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.storage_implementation import get_storage
from db.cache_implementation import get_cache
from models.film import Film
from models.person import Person

CACHE_EXPIRE = 60  # seconds


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.cache = redis
        self.storage = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._person_from_storage(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        prefix = 'person:'
        data = await self.cache.get(prefix + person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _person_search_from_cache(self, query: dict) -> List[str]:
        prefix = 'person_search'
        query_json = json.dumps(query)
        ids = await self.cache.get(':'.join((prefix, query_json)))
        if not ids:
            return []
        return json.loads(ids)

    async def _person_from_storage(self, person_id: str) -> Optional[Person]:
        try:
            data = await self.storage.get('persons', person_id)
        except NotFoundError:
            return None
        data = data["_source"]
        data['films'] = await self._get_created_filmworks(person_id)
        return Person.parse_obj(data)

    async def _put_person_to_cache(self, person: Person):
        prefix = 'person:'
        await self.cache.set(prefix + person.id, person.json(), expire=CACHE_EXPIRE)

    async def _put_search_to_cache(self, query, ids):
        prefix = 'person_search'
        query = json.dumps(query)
        ids = json.dumps(ids)
        await self.cache.set(':'.join((prefix, query)), ids, expire=CACHE_EXPIRE)

    async def _get_actor_filmworks(self, person_id: str) -> Optional[List[dict]]:
        """
        Find films where given person played some role
        :param person_id:
        :return: List[dict]: [{"uuid": filmwork_uuid, "role": actor_role}, ...]
        """
        films = await self._get_filmworks_by_person_job(person_id, 'actor')
        # TODO: add role when it will exist in index schema
        films = [{"uuid": film.id, "role": None} for film in films]
        return films

    async def _get_created_filmworks(self, person_id: str) -> Optional[List[dict]]:
        """
        Find films which given person did create
        :param person_id:
        :return: List[dict]
        """
        roles = ['writer', 'director', 'actor']
        all_films = []
        for role in roles:
            films = await self._get_filmworks_by_person_job(person_id, role)
            films = [{"id": film.id, "role": role} for film in films]
            all_films.extend(films)
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
        search_results = await self.storage.search(body=query, index='movies')
        films = [Film.parse_obj(film["_source"])
                 for film in search_results["hits"]["hits"]]
        return films

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
        ids = await self._person_search_from_cache(query)
        if not ids:
            search_results = await self.storage.search(body=query, index='persons')
            ids = [result["_id"] for result in search_results["hits"]["hits"]]
            await self._put_search_to_cache(query, ids)
        persons = [await self.get_by_id(person_id) for person_id in ids]
        if not persons:
            return None
        return persons


@lru_cache()
def get_person_service(
        cache: Redis = Depends(get_cache),
        storage: AsyncElasticsearch = Depends(get_storage),
) -> PersonService:
    return PersonService(cache, storage)
