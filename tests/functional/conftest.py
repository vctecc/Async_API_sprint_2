import os
from dataclasses import dataclass

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.client import SnapshotClient
from multidict import CIMultiDictProxy

from functional.settings import TestSettings

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


@pytest.fixture(autouse=True)
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
        if params is None:
            params = {}
        url = "http://" + SERVICE_URL + API_URL + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner
