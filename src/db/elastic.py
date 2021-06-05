from typing import ClassVar

from elasticsearch import AsyncElasticsearch
from db.storage import Storage


es: AsyncElasticsearch = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return es


class AsyncElasticsearchStorage(Storage):

    def __init__(self, model: ClassVar, index: str):
        super().__init__()
        self.model = model
        self.index = index

    def __call__(self):
        return self

    @property
    def client(self) -> AsyncElasticsearch:
        return es

    async def get(self, doc_id: str):
        document = await self.client.get(self.index, doc_id)
        return self.model(**document['_source'])

    async def get_many(self, **kwargs):
        pass

    async def search(self, **kwargs):
        pass
