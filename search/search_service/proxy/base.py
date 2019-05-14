from abc import ABCMeta, abstractmethod

from search_service.models.search_result import SearchResult


class BaseProxy(metaclass=ABCMeta):
    """
    Base Proxy, which behaves like an interface for all
    the proxy clients available in the amundsen search service
    """

    @abstractmethod
    def fetch_search_results_with_field(self, *,
                                        query_term: str,
                                        field_name: str,
                                        field_value: str,
                                        page_index: int = 0) -> SearchResult:
        pass

    @abstractmethod
    def fetch_search_results(self, *,
                             query_term: str,
                             page_index: int = 0) -> SearchResult:
        pass
