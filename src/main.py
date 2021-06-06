import logging

import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import film, person
from core import config
from core.logger import LOGGING
from db import storage_implementation, cache_implementation

# TODO: Добавить конфиг для DEBUG режима.

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    cache_implementation.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)
    storage_implementation.es = AsyncElasticsearch(hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"])


@app.on_event("shutdown")
async def shutdown():
    await cache_implementation.redis.close()
    await storage_implementation.es.close()


# Подключаем роутер к серверу, указав префикс /v1/film
# Теги указываем для удобства навигации по документации
app.include_router(film.router, prefix="/v1/film", tags=["film"])
app.include_router(film.router, prefix="/v1/genre", tags=["genre"])
app.include_router(person.router, prefix="/v1/person", tags=["person"])
app.include_router(person.router, prefix="/v1/person/search", tags=["person"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
