import abc
import logging

logger = logging.getLogger(__name__)


class Storage(abc.ABC):

    @abc.abstractmethod
    def client(self):
        pass

    @abc.abstractmethod
    async def get(self, **kwargs):
        pass

    @abc.abstractmethod
    async def get_many(self, **kwargs):
        pass

    @abc.abstractmethod
    async def search(self, **kwargs):
        pass