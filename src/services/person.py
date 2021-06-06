from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
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
            await self._put_to_cache(person)
        return person

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.cache.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _person_from_storage(self, person_id: str) -> Optional[Person]:
        data = await self.storage.get('persons', person_id)
        if not data:
            return None
        data = data["_source"]
        data['actor_in'] = await self._get_filmworks_by_actor(person_id)
        data['creator_in'] = await self._get_filmworks_by_creator(person_id)
        return Person.parse_obj(data)

    async def _put_to_cache(self, person: Person):
        await self.cache.set(person.id, person.json(), expire=CACHE_EXPIRE)

    async def _get_filmworks_by_actor(self, person_id: str) -> Optional[List[dict]]:
        """
        Find films where given person played some role
        :param person_id:
        :return: List[dict]: [{"uuid": filmwork_uuid, "role": actor_role}, ...]
        """
        query = {
            'query': {
                'nested': {
                    'path': 'actors',
                    'query': {
                        'match': {
                            'actors.id': person_id
                        }
                    }
                }
            }
        }
        search_results = await self.storage.search(body=query, index='movies')
        films = [{"uuid": film['_id'], "role": None} for film in search_results["hits"]["hits"]]
        return films

    async def _get_filmworks_by_creator(self, person_id: str) -> Optional[List[dict]]:
        """
        Find films which given person did create
        :param person_id:
        :return: List[dict]
        """
        jobs = ['writer', 'director', 'actor']
        all_films = []
        for job in jobs:
            query = {
                'query': {
                    'nested': {
                        'path': f'{job}s',
                        'query': {
                            'match': {
                                f'{job}s.id': person_id
                            }
                        }
                    }
                }
            }
            search_results = await self.storage.search(body=query, index='movies')
            films = [{"uuid": film['_id'], "job": job} for film in search_results["hits"]["hits"]]
            all_films.extend(films)
        return all_films


@lru_cache()
def get_person_service(
        cache: Redis = Depends(get_redis),
        storage: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(cache, storage)
