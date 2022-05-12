# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock

from amundsen_common.models.search import Filter, SearchResponse
from elasticsearch_dsl import Search
from elasticsearch_dsl.response import Response

from search_service import create_app
from search_service.proxy.es_proxy_v2 import ElasticsearchProxyV2, Resource
from tests.unit.proxy.v2.fixtures_v2 import (
    FILTER_QUERY, RESPONSE_1, RESPONSE_2, TERM_FILTERS_QUERY, TERM_QUERY,
)


class TestElasticsearchProxyV2(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        mock_index = 'mock_index'
        mock_elasticsearch_client = MagicMock()
        mock_elasticsearch_client.indices.get_alias.return_value = {
            mock_index: {}
        }
        mock_elasticsearch_client.indices.get_mapping.return_value = {
            mock_index: {
                'mappings': {}
            }
        }
        self.es_proxy = ElasticsearchProxyV2(host='mock_host',
                                             user='mock_user',
                                             password='mock_password',
                                             client=mock_elasticsearch_client,
                                             page_size=10)

    def test_build_elasticsearch_query_term_filters(self) -> None:
        actual = self.es_proxy._build_elasticsearch_query(resource=Resource.FEATURE,
                                                          query_term="mock_feature",
                                                          filters=[
                                                              Filter(name='badges',
                                                                     values=['pii'],
                                                                     operation='AND'),
                                                              Filter(name='feature_group',
                                                                     values=['test_group', 'mock_group'],
                                                                     operation='OR')])
        expected = TERM_FILTERS_QUERY

        self.assertDictEqual(actual.to_dict(), expected)

    def test_build_elasticsearch_query_term_no_filters(self) -> None:
        actual = self.es_proxy._build_elasticsearch_query(resource=Resource.TABLE,
                                                          query_term="mock_table",
                                                          filters=[])
        expected = TERM_QUERY

        self.assertDictEqual(actual.to_dict(), expected)

    def test_build_elasticsearch_query_just_filters(self) -> None:
        actual = self.es_proxy._build_elasticsearch_query(resource=Resource.DASHBOARD,
                                                          query_term="",
                                                          filters=[
                                                              Filter(name='name',
                                                                     values=['mock_dashobard_*'],
                                                                     operation='OR'),
                                                              Filter(name='group_name',
                                                                     values=['test_group', 'mock_group'],
                                                                     operation='OR'),
                                                              Filter(name='tag',
                                                                     values=['tag_*', 'tag_2'],
                                                                     operation='AND')
                                                          ])
        expected = FILTER_QUERY
        self.assertDictEqual(actual.to_dict(), expected)

    def test_es_search_format_response_1_resource(self) -> None:
        mock_es_dsl_search = Search()
        mock_es_dsl_responses = [Response(mock_es_dsl_search, r) for r in RESPONSE_1]
        formatted_response = self.es_proxy._format_response(page_index=0,
                                                            results_per_page=10,
                                                            responses=mock_es_dsl_responses,
                                                            resource_types=[Resource.TABLE, Resource.USER])
        expected = SearchResponse(msg='Success',
                                  page_index=0,
                                  results_per_page=10,
                                  results={
                                      "table": {
                                          "results": [
                                              {
                                                  "key": "mock_db://mock_cluster.mock_schema/mock_table_1",
                                                  "description": "mock table description",
                                                  "badges": [
                                                      "pii",
                                                      "beta"
                                                  ],
                                                  "tag": [
                                                      "mock_tag_1",
                                                      "mock_tag_2",
                                                      "mock_tag_3"
                                                  ],
                                                  "schema": "mock_schema",
                                                  "table": "mock_table_1",
                                                  "column": [
                                                      "mock_col_1",
                                                      "mock_col_2",
                                                      "mock_col_3"
                                                  ],
                                                  "database": "mock_db",
                                                  "cluster": "mock_cluster",
                                                  "search_score": 804.52716,
                                                  "resource_type": "table"
                                              },
                                              {
                                                  "key": "mock_db://mock_cluster.mock_schema/mock_table_2",
                                                  "description": "mock table description",
                                                  "badges": [],
                                                  "tag": [
                                                      "mock_tag_4",
                                                      "mock_tag_5",
                                                      "mock_tag_6"
                                                  ],
                                                  "schema": "mock_schema",
                                                  "table": "mock_table_2",
                                                  "column": [
                                                      "mock_col_1",
                                                      "mock_col_2",
                                                      "mock_col_3"
                                                  ],
                                                  "database": "mock_db",
                                                  "cluster": "mock_cluster",
                                                  "search_score": 9.104584,
                                                  "resource_type": "table"
                                              }
                                          ],
                                          "total_results": 2
                                      },
                                      "user": {
                                          "results": [],
                                          "total_results": 0
                                      }
                                  },
                                  status_code=200)

        self.assertEqual(formatted_response, expected)

    def test_es_search_format_response_multiple_resources(self) -> None:
        mock_es_dsl_search = Search()
        mock_es_dsl_responses = [Response(mock_es_dsl_search, r) for r in RESPONSE_2]
        formatted_response = self.es_proxy._format_response(page_index=0,
                                                            results_per_page=10,
                                                            responses=mock_es_dsl_responses,
                                                            resource_types=[
                                                                Resource.TABLE,
                                                                Resource.USER,
                                                                Resource.FEATURE])
        expected = SearchResponse(msg='Success',
                                  page_index=0,
                                  results_per_page=10,
                                  results={
                                      "table": {
                                          "results": [
                                              {
                                                  "key": "mock_db://mock_cluster.mock_schema/mock_table_1",
                                                  "description": "mock table description",
                                                  "badges": [
                                                      "pii",
                                                      "beta"
                                                  ],
                                                  "tag": [
                                                      "mock_tag_1",
                                                      "mock_tag_2",
                                                      "mock_tag_3"
                                                  ],
                                                  "schema": "mock_schema",
                                                  "table": "mock_table_1",
                                                  "column": [
                                                      "mock_col_1",
                                                      "mock_col_2",
                                                      "mock_col_3"
                                                  ],
                                                  "database": "mock_db",
                                                  "cluster": "mock_cluster",
                                                  "search_score": 804.52716,
                                                  "resource_type": "table"
                                              },
                                              {
                                                  "key": "mock_db://mock_cluster.mock_schema/mock_table_2",
                                                  "description": "mock table description",
                                                  "badges": [],
                                                  "tag": [
                                                      "mock_tag_4",
                                                      "mock_tag_5",
                                                      "mock_tag_6"
                                                  ],
                                                  "schema": "mock_schema",
                                                  "table": "mock_table_2",
                                                  "column": [
                                                      "mock_col_1",
                                                      "mock_col_2",
                                                      "mock_col_3"
                                                  ],
                                                  "database": "mock_db",
                                                  "cluster": "mock_cluster",
                                                  "search_score": 9.104584,
                                                  "resource_type": "table"
                                              }
                                          ],
                                          "total_results": 2
                                      },
                                      "user": {
                                          "results": [
                                              {
                                                  "full_name": "Allison Suarez Miranda",
                                                  "first_name": "Allison",
                                                  "last_name": "Suarez Miranda",
                                                  "email": "mock_user@amundsen.com",
                                                  "search_score": 61.40606,
                                                  "resource_type": "user"
                                              }
                                          ],
                                          "total_results": 1
                                      },
                                      "feature": {
                                          "results": [
                                              {
                                                  "key": "none/feature_1/1",
                                                  "feature_group": "fg_2",
                                                  "feature_name": "feature_1",
                                                  "description": "mock feature description",
                                                  "entity": None,
                                                  "status": "active",
                                                  "version": 1,
                                                  "availability": None,
                                                  "tags": [],
                                                  "badges": [],
                                                  "search_score": 62.66787,
                                                  "resource_type": "feature"
                                              },
                                              {
                                                  "key": "fg_2/feature_2/1",
                                                  "feature_group": "fg_2",
                                                  "feature_name": "feature_2",
                                                  "description": "mock feature description",
                                                  "entity": None,
                                                  "status": "active",
                                                  "version": 1,
                                                  "availability": None,
                                                  "tags": [],
                                                  "badges": [],
                                                  "search_score": 62.66787,
                                                  "resource_type": "feature"
                                              },
                                              {
                                                  "key": "fg_3/feature_3/2",
                                                  "feature_group": "fg_3",
                                                  "feature_name": "feature_3",
                                                  "description": "mock feature description",
                                                  "entity": None,
                                                  "status": "active",
                                                  "version": 2,
                                                  "availability": None,
                                                  "tags": [],
                                                  "badges": [
                                                      "pii"
                                                  ],
                                                  "search_score": 62.66787,
                                                  "resource_type": "feature"
                                              }
                                          ],
                                          "total_results": 3
                                      }
                                  },
                                  status_code=200)

        self.assertEqual(formatted_response, expected)
