"""
Auth integration
"""
from http import HTTPStatus

import aiohttp
from aiohttp import ClientConnectionError
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBearer

from core.config import AUTH_URL

security = HTTPBearer()


def role_validator_factory(roles=("user",)):
    async def token_is_valid(credentials: HTTPBasicCredentials = Depends(security), ):
        async with aiohttp.ClientSession() as session:
            data = {"roles": roles}
            try:
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
            except ClientConnectionError:
                # TODO: do it pretty with some retries
                raise HTTPException(status_code=HTTPStatus.GATEWAY_TIMEOUT,
                                    detail="Auth service is unavailable")
            return credentials.credentials
    return token_is_valid
