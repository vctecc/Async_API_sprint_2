import json
import os
from dataclasses import dataclass

import aiofiles
import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.client import SnapshotClient
from multidict import CIMultiDictProxy

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


async def create_index(es_client, name, scheme_path, data_path):
    body = json.load(open(scheme_path))
    data = json.load(open(data_path))
    await es_client.indices.create(index=name, body=body, ignore=400)
    await es_client.bulk(body=data, index=name)

    items = {}
    # FIXME add timeout
    while not items.get("count"):
        items = await es_client.count(index=name)


@pytest.fixture()
async def create_movie_index(es_client, redis_client):
    name = "movies"
    data_path = settings.load_data_dir.joinpath("movies.json")
    scheme_path = settings.es_schemes_dir.joinpath("movies.json")
    await create_index(es_client, name, scheme_path, data_path)
    yield
    await es_client.indices.delete(index=name, ignore=[400, 404])


@pytest.fixture(scope="function")
async def expected_json_response(request):
    """Load expected response from json file with same filename as function name"""
    file = settings.expected_response_dir.joinpath(f"{request.node.name}.json")
    async with aiofiles.open(file) as f:
        content = await f.read()
        response = json.loads(content)
    return response
