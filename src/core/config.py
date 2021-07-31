import os
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "Movies API")

# Тип окружения (development при True, production при False)
DEV = os.getenv("DEV") or False

#
AUTH_HOST = os.getenv("AUTH_HOST", "auth-api")
AUTH_PORT = os.getenv("AUTH_PORT", "5000")
AUTH_ENDPOINT = os.getenv("AUTH_ENDPOINT", "api/v1/auth/check")
AUTH_URL = f"http://{AUTH_HOST}:{AUTH_PORT}/{AUTH_ENDPOINT}"

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_BACKOFF_TIME = int(os.getenv("CACHE_BACKOFF_TIME", 10))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "127.0.0.1")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))
STORAGE_BACKOFF_TIME = int(os.getenv("STORAGE_BACKOFF_TIME", 10))

BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", 0.5))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

minute = 60

DEFAULT_CACHE_EXPIRE = int(os.getenv("DEFAULT_CACHE_EXPIRE", 5 * minute))
FILM_CACHE_EXPIRE = int(os.getenv("FILM_CACHE_EXPIRE", DEFAULT_CACHE_EXPIRE))
PERSON_CACHE_EXPIRE = int(os.getenv("PERSON_CACHE_EXPIRE", DEFAULT_CACHE_EXPIRE))
GENRE_CACHE_EXPIRE = int(os.getenv("GENRE_CACHE_EXPIRE", DEFAULT_CACHE_EXPIRE))
GENRE_POPULARITY_CACHE_EXPIRE = int(os.getenv("GENRE_POPULARITY_CACHE_EXPIRE", DEFAULT_CACHE_EXPIRE))

FILM_WORKS_INDEX = os.getenv("FILM_WORKS_INDEX", "movies")
PERSONS_INDEX = os.getenv("PERSONS_INDEX", "persons")
GENRES_INDEX = os.getenv("GENRES_INDEX", "genres")

FILM_PAGE_SIZE = 10
FILM_PAGE_NUMBER = 1
