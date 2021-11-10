# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from unittest import TestCase

from mock import MagicMock, patch

from search_service import create_app
from search_service.models.results import SearchResult
from search_service.models.base import Base


class TestSearchAPI(TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.Config')
        self.app_context = self.app.app_context()
        self.app_context.push()

        # self.mock_client = patch('search_service.proxy.search.ElasticsearchProxy')
        # self.mock_proxy = self.mock_client.start().return_value = Mock()

        self.mock_term = 'test'
        self.url = '/search_resources'

    def tear_down(self) -> None:
        self.app_context.pop()

    @patch('search_service.api.search.reqparse.RequestParser')
    @patch('search_service.proxy.es_search_proxy.ElasticsearchProxy')
    def test_post(self, get_proxy: MagicMock, RequestParser: MagicMock) -> None:

        from search_service.models.results import SearchResultSchema, SearchResult, ResourceResults
        from search_service.models.resources import Table
        table_result = Table(id='test_id',
                                    key='test_key',
                                    name='test_name',
                                    search_score=123,
                                    schema='test_schema',
                                    database='test_db',
                                    cluster='test_cluster')
        table_results = ResourceResults(total_results=1, results=[table_result])
        r = SearchResultSchema().dump(SearchResult(page_index=0,
                                                 results_per_page=10,
                                                 search_results={'tables': table_results}))
        print(r)
        self.mock_proxy = get_proxy()

        RequestParser().parse_args.return_value = dict(query_term=self.mock_term)

        

        self.mock_proxy.get_search_results.return_value = \
            SearchResult(page_index=0, results_per_page=10, search_results={})
        # print(self.mock_proxy.get_search_results.return_value)

        response = self.app.test_client().post(self.url)

        # print(response)
        # print(response.json)

        expected_response = {
            "page_index": 0,
            "results_per_page": 10,
            "search_results": {}
        }
        # print(expected_response)
        self.assertEqual(response.json, expected_response)
