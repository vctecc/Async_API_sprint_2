from db.storage import Storage
from db.es_storage import AsyncElasticsearchStorage


def get_current_storage(**kwargs) -> Storage:
    return AsyncElasticsearchStorage(**kwargs)
