import backoff
import redis

from functional.settings import TestSettings

settings = TestSettings()
REDIS_WAIT_TIME = 300


# TODO: add logs
@backoff.on_exception(backoff.expo,
                      redis.exceptions.ConnectionError,
                      max_time=REDIS_WAIT_TIME)
def wait_for_redis(r):
    r.ping()


if __name__ == "__main__":
    host = settings.redis_host
    port = settings.redis_port
    r = redis.Redis(host=host, port=port)

    wait_for_redis(r)
