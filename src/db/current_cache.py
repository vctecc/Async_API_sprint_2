from db.cache import Cache
from db.redis_cache import RedisCache


def get_current_cache(**kwargs) -> Cache:
    return RedisCache(**kwargs)
