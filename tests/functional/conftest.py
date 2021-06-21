import os
import json

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from elasticsearch.client import SnapshotClient
from multidict import CIMultiDictProxy
from pydantic import BaseModel
from dataclasses import dataclass

from .settings import TestSettings

settings = TestSettings()
API_URL = settings.api_url
SERVICE_URL = settings.service_url


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
async def es_client():
    host = settings.es_host + ":" + settings.es_port
    client = AsyncElasticsearch(hosts=host)
    yield client
    await client.close()


@pytest.fixture
async def redis_client():
    redis = await aioredis.create_redis_pool(
        (settings.redis_host, settings.redis_port),
        minsize=10, maxsize=20
    )
    yield redis
    redis.close()


@pytest.fixture()
async def es_from_snapshot(es_client):
    """
    Fill ElasticSearch data from snapshot and cleanup after tests.
    """
    snapshots = SnapshotClient(es_client)
    body = {
        "type": "fs",
        "settings": {
            "location": os.path.join(settings.es_snapshot_loc, settings.es_snapshot_repo)
        }
    }
    await snapshots.create_repository(repository=settings.es_snapshot_repo,
                                      body=body,
                                      verify=True)
    await snapshots.restore(repository=settings.es_snapshot_repo,
                            snapshot="snapshot_1",
                            wait_for_completion=True)

    yield
    # Cleanup
    indices = await es_client.indices.get_alias()
    for index in indices.keys():
        await es_client.indices.delete(index=index)
    await snapshots.delete_repository(repository=settings.es_snapshot_repo)


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        url = "http://" + SERVICE_URL + API_URL + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


async def create_index(es_client, name, body, data):
    await es_client.indices.create(index=name, body=body, ignore=400)
    await async_bulk(es_client, data, index=name, doc_type="_doc")

    movies_items = {}
    # FIXME add timeout
    while not movies_items.get('count'):
        movies_items = await es_client.count(index=name)


@pytest.fixture()
async def create_movie_index(es_client, redis_client):
    name = 'movies'
    data_path = 'tests/functional/testdata/load_data/films.json'
    index_path = 'tests/functional/testdata/schemes/films.json'

    index_body = json.load(open(index_path))
    data = json.load(open(data_path))
    await redis_client.flushall()
    await create_index(es_client, name, index_body, data)
    yield
    await es_client.indices.delete(index=name, ignore=[400, 404])
