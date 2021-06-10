from http import HTTPStatus
from typing import ClassVar

import elasticsearch
from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException

from db.storage import Storage

es: AsyncElasticsearch = None


class AsyncElasticsearchStorage(Storage):

    def __init__(self, model: ClassVar, index: str):
        super().__init__()
        self.model = model
        self.index = index

    @property
    def client(self) -> AsyncElasticsearch:
        return es

    async def get(self, doc_id: str):
        try:
            document = await self.client.get(self.index, doc_id)
            print(document)

        except elasticsearch.exceptions.NotFoundError:
            return None
        return self.model(**document["_source"])

    async def get_many(self, **kwargs):
        pass

    async def search(self, query: dict):
        try:
            result = await self.client.search(index=self.index, body=query)
        except elasticsearch.exceptions.RequestError as re:
            if re.error == "search_phase_execution_exception":
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Malformed request")
            raise re

        if not result["hits"]["total"]["value"]:
            return []

        items = [self.model(**hit["_source"]) for hit in result["hits"]["hits"]]
        return items

    async def count(self, query: dict) -> int:
        """
        Возвращает количество элементов, найденных по запросу. Работает быстрее, чем search.
        :param query: словарь с параметрами запроса согласно ES DSL.
        :return: количество найденных элементов.
        """
        try:
            result = await self.client.count(index=self.index, body=query)
        except elasticsearch.exceptions.RequestError as re:
            if re.error == "count_phase_execution_exception":
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Malformed request")
            raise re
        return result["count"]
