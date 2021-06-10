import abc
import logging

logger = logging.getLogger(__name__)


class Storage(abc.ABC):

    @abc.abstractmethod
    def client(self):
        pass

    @abc.abstractmethod
    async def get(self, doc_id: str):
        pass

    @abc.abstractmethod
    async def search(self, query: dict):
        pass
