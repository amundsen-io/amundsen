# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from search_service.models.results import SearchResult


class ElasticsearchProxy():
    def __init__(self, *,
                 host: str = None,
                 user: str = '') -> None:
        # TODO actually implement this
        self.host = host
        self.user = user

    def get_search_results(self) -> SearchResult:
        return None