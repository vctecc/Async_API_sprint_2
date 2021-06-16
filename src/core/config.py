import os
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "Movies API")

# Тип окружения (development при True, production при False)
DEV = os.getenv("DEV") or False

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "127.0.0.1")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

minute = 60

DEFAULT_CACHE_EXPIRE = os.getenv("DEFAULT_CACHE_EXPIRE", 5 * minute)
FILM_CACHE_EXPIRE = os.getenv("FILM_CACHE_EXPIRE", DEFAULT_CACHE_EXPIRE)
PERSON_CACHE_EXPIRE = os.getenv("PERSON_CACHE_EXPIRE", DEFAULT_CACHE_EXPIRE)
GENRE_CACHE_EXPIRE = os.getenv("GENRE_CACHE_EXPIRE", DEFAULT_CACHE_EXPIRE)
GENRE_POPULARITY_CACHE_EXPIRE = os.getenv("GENRE_POPULARITY_CACHE_EXPIRE", DEFAULT_CACHE_EXPIRE)

FILM_WORKS_INDEX = os.getenv("FILM_WORKS_INDEX", "films")
PERSONS_INDEX = os.getenv("PERSONS_INDEX", "persons")
GENRES_INDEX = os.getenv("GENRES_INDEX", "genres")

FILM_PAGE_SIZE = 10
FILM_PAGE_NUMBER = 10