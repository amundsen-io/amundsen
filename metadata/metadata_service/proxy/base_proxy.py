from abc import ABCMeta, abstractmethod

from metadata_service.entity.table_detail import Table


class BaseProxy(metaclass=ABCMeta):
    """
    Base Proxy, which behaves like an interface for all
    the proxy clients available in the amundsen metadata service
    """
    @abstractmethod
    def get_table(self, *, table_uri: str) -> Table:
        pass
