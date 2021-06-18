from dataclasses import dataclass

import aiohttp
import pytest
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
def make_get_request(session):
    async def inner(method: str, params: dict) -> HTTPResponse:
        url = "http://" + SERVICE_URL + API_URL + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner
