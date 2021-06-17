import backoff
import elasticsearch
from elasticsearch.client import Elasticsearch

from tests.functional.settings import TestSettings

settings = TestSettings()
ES_WAIT_TIME = 300


# TODO: add logs
@backoff.on_exception(backoff.expo,
                      elasticsearch.ConnectionError,
                      max_time=ES_WAIT_TIME)
def wait_for_es(es):
    if not es.ping():
        raise elasticsearch.ConnectionError


if __name__ == "__main__":
    host = settings.es_host + ":" + settings.es_port
    es = Elasticsearch([host])

    wait_for_es(es)
