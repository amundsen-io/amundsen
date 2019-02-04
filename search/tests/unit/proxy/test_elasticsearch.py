import unittest
from unittest.mock import patch, MagicMock
from typing import Iterable

from search_service import create_app
from search_service.proxy.elasticsearch import ElasticsearchProxy
from search_service.models.search_result import SearchResult
from search_service.models.table import Table


class MockSearchResult:
    def __init__(self, *,
                 table_name: str,
                 table_key: str,
                 table_description: str,
                 cluster: str,
                 database: str,
                 schema_name: str,
                 column_names: Iterable[str],
                 tag_names: Iterable[str],
                 table_last_updated_epoch: int) -> None:
        self.table_name = table_name
        self.table_key = table_key
        self.table_description = table_description
        self.cluster = cluster
        self.database = database
        self.schema_name = schema_name
        self.column_names = column_names
        self.tag_names = tag_names
        self.table_last_updated_epoch = table_last_updated_epoch


class TestElasticsearchProxy(unittest.TestCase):

    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

        mock_elasticsearch_client = MagicMock()
        self.es_proxy = ElasticsearchProxy(elasticsearch_client=mock_elasticsearch_client)

        self.mock_result1 = MockSearchResult(table_name='test_table',
                                             table_key='test_key',
                                             table_description='test_description',
                                             cluster='gold',
                                             database='test_db',
                                             schema_name='test_schema',
                                             column_names=['test_col1', 'test_col2'],
                                             tag_names=[],
                                             table_last_updated_epoch=1527283287)

        self.mock_result2 = MockSearchResult(table_name='test_table2',
                                             table_key='test_key2',
                                             table_description='test_description2',
                                             cluster='gold',
                                             database='test_db2',
                                             schema_name='test_schema2',
                                             column_names=['test_col1', 'test_col2'],
                                             tag_names=[],
                                             table_last_updated_epoch=1527283287)

        self.mock_result3 = Table(name='test_table3',
                                  key='test_key3',
                                  description='test_description3',
                                  cluster='gold',
                                  database='test_db3',
                                  schema_name='test_schema3',
                                  column_names=['test_col1', 'test_col2'],
                                  tags=['match'],
                                  last_updated_epoch=1527283287)

    @patch('elasticsearch_dsl.Search.execute')
    def test_search_with_empty_query_string(self, mock_search: MagicMock) -> None:

        expected = SearchResult(total_results=0, results=[])
        result = self.es_proxy.fetch_search_results(query_term='')

        # check the output was empty list
        self.assertDictEqual(vars(result), vars(expected),
                             "Received non-empty search results!")

        # ensure elasticsearch_dsl Search endpoint was not called
        # assert_not_called doesn't work. See here: http://engineroom.trackmaven.com/blog/mocking-mistakes/
        self.assertTrue(mock_search.call_count == 0)

    @patch('elasticsearch_dsl.Search.execute')
    def test_search_with_empty_result(self,
                                      mock_search: MagicMock) -> None:

        mock_results = MagicMock()
        mock_results.hits.total = 0
        mock_search.return_value = mock_results

        expected = SearchResult(total_results=0, results=[])
        result = self.es_proxy.fetch_search_results(query_term='test_query_term')
        self.assertDictEqual(vars(result), vars(expected),
                             "Received non-empty search results!")

    @patch('elasticsearch_dsl.Search.execute')
    def test_search_with_one_result(self,
                                    mock_search: MagicMock) -> None:

        mock_results = MagicMock()
        mock_results.hits.total = 1
        mock_results.__iter__.return_value = [self.mock_result1]
        mock_search.return_value = mock_results

        expected = SearchResult(total_results=1,
                                results=[Table(name='test_table',
                                               key='test_key',
                                               description='test_description',
                                               cluster='gold',
                                               database='test_db',
                                               schema_name='test_schema',
                                               column_names=['test_col1', 'test_col2'],
                                               tags=[],
                                               last_updated_epoch=1527283287)])

        resp = self.es_proxy.fetch_search_results(query_term='test_query_term')

        self.assertEquals(resp.total_results, expected.total_results,
                          "search result is not of length 1")
        self.assertIsInstance(resp.results[0],
                              Table,
                              "Search result received is not of 'Table' type!")
        self.assertDictEqual(vars(resp.results[0]), vars(expected.results[0]),
                             "Search Result doesn't match with expected result!")

    @patch('elasticsearch_dsl.Search.execute')
    def test_search_with_multiple_result(self,
                                         mock_search: MagicMock) -> None:

        mock_results = MagicMock()
        mock_results.hits.total = 2
        mock_results.__iter__.return_value = [self.mock_result1, self.mock_result2]
        mock_search.return_value = mock_results

        expected = SearchResult(total_results=2,
                                results=[Table(name='test_table',
                                               key='test_key',
                                               description='test_description',
                                               cluster='gold',
                                               database='test_db',
                                               schema_name='test_schema',
                                               column_names=['test_col1', 'test_col2'],
                                               tags=[],
                                               last_updated_epoch=1527283287),
                                         Table(name='test_table2',
                                               key='test_key2',
                                               description='test_description2',
                                               cluster='gold',
                                               database='test_db2',
                                               schema_name='test_schema2',
                                               column_names=['test_col1', 'test_col2'],
                                               tags=[],
                                               last_updated_epoch=1527283287)])

        resp = self.es_proxy.fetch_search_results(query_term='test_query_term')

        self.assertEquals(resp.total_results, expected.total_results,
                          "search result is not of length 2")
        for i in range(2):
            self.assertIsInstance(resp.results[i],
                                  Table,
                                  "Search result received is not of 'Table' type!")
            self.assertDictEqual(vars(resp.results[i]),
                                 vars(expected.results[i]),
                                 "Search result doesn't match with expected result!")

    @patch('search_service.proxy.elasticsearch.ElasticsearchProxy._search_helper')
    def test_search_match_with_field(self,
                                     mock_search: MagicMock) -> None:

        mock_search.return_value = SearchResult(total_results=1,
                                                results=[self.mock_result3])

        expected = SearchResult(total_results=1,
                                results=[Table(name='test_table3',
                                               key='test_key3',
                                               description='test_description3',
                                               cluster='gold',
                                               database='test_db3',
                                               schema_name='test_schema3',
                                               column_names=['test_col1', 'test_col2'],
                                               tags=['match'],
                                               last_updated_epoch=1527283287)])

        resp = self.es_proxy.fetch_search_results_with_field(query_term='test_query_term',
                                                             field_name='tag_names',
                                                             field_value='match')
        self.assertEquals(resp.total_results, expected.total_results)

        self.assertDictEqual(vars(resp.results[0]),
                             vars(expected.results[0]),
                             "Search result doesn't match with expected result!")

    @patch('search_service.proxy.elasticsearch.ElasticsearchProxy._search_helper')
    def test_search_not_match_with_field(self,
                                         mock_search: MagicMock) -> None:

        mock_search.return_value = SearchResult(total_results=0,
                                                results=[])

        resp = self.es_proxy.fetch_search_results_with_field(query_term='test_query_term',
                                                             field_name='tag_names',
                                                             field_value='match')
        self.assertEquals(resp.total_results, 0)

    @patch('search_service.proxy.elasticsearch.ElasticsearchProxy._search_wildcard_helper')
    def test_search_regex_match_field(self,
                                      mock_search: MagicMock) -> None:
        mock_search.return_value = SearchResult(total_results=1,
                                                results=[self.mock_result3])

        expected = SearchResult(total_results=1,
                                results=[Table(name='test_table3',
                                               key='test_key3',
                                               description='test_description3',
                                               cluster='gold',
                                               database='test_db3',
                                               schema_name='test_schema3',
                                               column_names=['test_col1', 'test_col2'],
                                               tags=['match'],
                                               last_updated_epoch=1527283287)])
        resp = self.es_proxy.fetch_search_results_with_field(query_term='test_query_term',
                                                             field_name='tag_names',
                                                             field_value='*match')
        self.assertEquals(resp.total_results, expected.total_results)

        self.assertDictEqual(vars(resp.results[0]),
                             vars(expected.results[0]),
                             "Search result doesn't match with expected result!")
