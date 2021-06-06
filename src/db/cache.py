import abc
import logging


logger = logging.getLogger(__name__)


class Cache(abc.ABC):

    @abc.abstractmethod
    def client(self):
        pass

    @abc.abstractmethod
    def get(self, key: str):
        pass

    @abc.abstractmethod
    def get_many(self, key):
        pass

    def get_query(self, query: str):
        pass

    @abc.abstractmethod
    def set(self, key: str, value, expire):
        pass
