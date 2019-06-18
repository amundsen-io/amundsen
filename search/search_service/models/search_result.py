from typing import List
from search_service.models.table import Table


class SearchTableResult:
    def __init__(self, *,
                 total_results: int,
                 results: List[Table]) -> None:
        self.total_results = total_results
        self.results = results

    def __repr__(self) -> str:
        return 'SearchTableResult(total_results={!r}, results{!r})'.format(self.total_results, self.results)
