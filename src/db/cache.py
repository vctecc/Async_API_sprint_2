import abc
import logging


logger = logging.getLogger(__name__)


class Cache(abc.ABC):
    def __call__(self):
        return self

    @abc.abstractmethod
    def client(self):
        pass

    @abc.abstractmethod
    async def get(self, key: str):
        pass

    @abc.abstractmethod
    async def get_custom_data(self, key: str):
        pass

    @abc.abstractmethod
    async def get_query(self, query: str):
        pass

    @abc.abstractmethod
    async def set(self, key: str, value: str, expire: int):
        pass
