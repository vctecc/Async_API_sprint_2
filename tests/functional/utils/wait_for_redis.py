import backoff
import redis

from functional.settings import TestSettings

settings = TestSettings()


@backoff.on_exception(backoff.expo,
                      redis.exceptions.ConnectionError,
                      max_time=settings.redis_wait_time)
def wait_for_redis(r):
    r.ping()


if __name__ == "__main__":
    host = settings.redis_host
    port = settings.redis_port
    r = redis.Redis(host=host, port=port)

    wait_for_redis(r)
