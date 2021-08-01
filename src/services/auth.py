"""
Auth integration
"""
from http import HTTPStatus

import aiohttp
import backoff
from aiohttp import ClientConnectionError
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBearer

from core.config import AUTH_BACKOFF_TIME, AUTH_URL, BACKOFF_FACTOR

security = HTTPBearer()


def giveup_handler(details):
    raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE)


def role_validator_factory(roles=("user",)):
    @backoff.on_exception(backoff.expo,
                          ClientConnectionError,
                          max_time=AUTH_BACKOFF_TIME,
                          factor=BACKOFF_FACTOR,
                          on_giveup=giveup_handler)
    async def token_is_valid(credentials: HTTPBasicCredentials = Depends(security), ):
        async with aiohttp.ClientSession() as session:
            data = {"roles": roles}
            async with session.get(AUTH_URL,
                                   json=data,
                                   headers={'Authorization': f'Bearer {credentials.credentials}'}) as response:
                if response.status == 200:
                    return True
                if response.status == 401:
                    raise HTTPException(status_code=HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED)
                if response.status == 403:
                    raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                        detail="Forbidden")
                else:
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                        detail=f"Auth response: {await response.json()}")
            return credentials.credentials
    return token_is_valid
