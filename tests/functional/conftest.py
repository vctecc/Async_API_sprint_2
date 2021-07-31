import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime

import aiofiles
import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.client import SnapshotClient
from elasticsearch.helpers import async_bulk
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


@pytest.fixture(scope="session")
async def es_client():
    host = settings.es_host + ":" + settings.es_port
    client = AsyncElasticsearch(hosts=host)
    yield client
    await client.close()


@pytest.fixture(scope="session")
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


def read_json_file(file_path):
    with open(file_path) as json_file:
        json_data = json.load(json_file)
    return json_data


async def create_index(es_client, index_name):
    index_path = settings.es_schemes_dir.joinpath(f"{index_name}.json")
    index = read_json_file(index_path)
    await es_client.indices.create(index=index_name, body=index, ignore=400)


async def load_data_in_index(es_client, index_name):
    data_path = settings.load_data_dir.joinpath(f"{index_name}.json")
    data = read_json_file(data_path)
    await async_bulk(es_client, data, index=index_name)

    items = {}

    start_time = datetime.now()

    while not items.get("count"):
        items = await es_client.count(index=index_name)
        seconds = (datetime.now() - start_time).seconds

        if seconds >= settings.load_index_timeout:
            raise TimeoutError(f"Time-out for loading data into ES index {index_name}.")


async def initialize_es_index(es_client, index_name):
    await create_index(es_client, index_name)
    await load_data_in_index(es_client, index_name)


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
async def initialize_environment(es_client, redis_client):
    for index in settings.es_indexes:
        await initialize_es_index(es_client, index)
    yield
    await redis_client.flushall()
    for index in settings.es_indexes:
        await es_client.indices.delete(index=index, ignore=[400, 404])


@pytest.fixture(scope="function")
async def expected_json_response(request):
    """Load expected response from json file with same filename as function name"""
    file = settings.expected_response_dir.joinpath(f"{request.node.name}.json")
    async with aiofiles.open(file) as f:
        content = await f.read()
        response = json.loads(content)
    return response
