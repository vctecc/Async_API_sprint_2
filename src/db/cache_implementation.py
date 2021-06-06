from aioredis import Redis

redis: Redis = None


# Функция понадобится при внедрении зависимостей
async def get_cache() -> Redis:
    return redis
