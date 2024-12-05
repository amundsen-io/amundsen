# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock

from amundsen_common.models.search import SearchResponse
from elasticsearch_dsl import Search
from elasticsearch_dsl.response import Response

from search_service.proxy.es_proxy_utils import create_search_response
from search_service.proxy.es_proxy_v2 import ElasticsearchProxyV2
from search_service.proxy.es_proxy_v2_1 import ElasticsearchProxyV2_1, Resource
from tests.unit.proxy.v2.fixtures_v2 import RESPONSE_1, RESPONSE_2
from tests.unit.proxy.v2_1.fixtures_v2_1 import ES_RESPONSE_HIGHLIGHTED


class TestESProxyUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_elasticsearch_client = MagicMock()

    def test_es_search_format_response_1_resource(self) -> None:
        mock_es_dsl_search = Search()
        mock_es_dsl_responses = [Response(mock_es_dsl_search, r) for r in RESPONSE_1]
        actual = create_search_response(
            page_index=0,
            results_per_page=10,
            responses=mock_es_dsl_responses,
            resource_types=[Resource.TABLE, Resource.USER],
            resource_to_field_mapping=ElasticsearchProxyV2.RESOURCE_TO_MAPPING,
        )
        expected = SearchResponse(
            msg="Success",
            page_index=0,
            results_per_page=10,
            results={
                "table": {
                    "results": [
                        {
                            "key": "mock_db://mock_cluster.mock_schema/mock_table_1",
                            "description": "mock table description",
                            "badges": ["pii", "beta"],
                            "tag": ["mock_tag_1", "mock_tag_2", "mock_tag_3"],
                            "schema": "mock_schema",
                            "table": "mock_table_1",
                            "column": ["mock_col_1", "mock_col_2", "mock_col_3"],
                            "database": "mock_db",
                            "cluster": "mock_cluster",
                            "search_score": 804.52716,
                            "resource_type": "table",
                            "highlight": {},
                        },
                        {
                            "key": "mock_db://mock_cluster.mock_schema/mock_table_2",
                            "description": "mock table description",
                            "badges": [],
                            "tag": ["mock_tag_4", "mock_tag_5", "mock_tag_6"],
                            "schema": "mock_schema",
                            "table": "mock_table_2",
                            "column": ["mock_col_1", "mock_col_2", "mock_col_3"],
                            "database": "mock_db",
                            "cluster": "mock_cluster",
                            "search_score": 9.104584,
                            "resource_type": "table",
                            "highlight": {},
                        },
                    ],
                    "total_results": 2,
                },
                "user": {"results": [], "total_results": 0},
            },
            status_code=200,
        )

        self.assertEqual(actual, expected)

    def test_es_search_format_response_multiple_resources(self) -> None:
        mock_es_dsl_search = Search()
        mock_es_dsl_responses = [Response(mock_es_dsl_search, r) for r in RESPONSE_2]
        actual = create_search_response(
            page_index=0,
            results_per_page=10,
            responses=mock_es_dsl_responses,
            resource_types=[Resource.TABLE, Resource.USER, Resource.FEATURE],
            resource_to_field_mapping=ElasticsearchProxyV2.RESOURCE_TO_MAPPING,
        )
        expected = SearchResponse(
            msg="Success",
            page_index=0,
            results_per_page=10,
            results={
                "table": {
                    "results": [
                        {
                            "key": "mock_db://mock_cluster.mock_schema/mock_table_1",
                            "description": "mock table description",
                            "badges": ["pii", "beta"],
                            "tag": ["mock_tag_1", "mock_tag_2", "mock_tag_3"],
                            "schema": "mock_schema",
                            "table": "mock_table_1",
                            "column": ["mock_col_1", "mock_col_2", "mock_col_3"],
                            "database": "mock_db",
                            "cluster": "mock_cluster",
                            "search_score": 804.52716,
                            "resource_type": "table",
                            "highlight": {},
                        },
                        {
                            "key": "mock_db://mock_cluster.mock_schema/mock_table_2",
                            "description": "mock table description",
                            "badges": [],
                            "tag": ["mock_tag_4", "mock_tag_5", "mock_tag_6"],
                            "schema": "mock_schema",
                            "table": "mock_table_2",
                            "column": ["mock_col_1", "mock_col_2", "mock_col_3"],
                            "database": "mock_db",
                            "cluster": "mock_cluster",
                            "search_score": 9.104584,
                            "resource_type": "table",
                            "highlight": {},
                        },
                    ],
                    "total_results": 2,
                },
                "user": {
                    "results": [
                        {
                            "full_name": "Allison Suarez Miranda",
                            "first_name": "Allison",
                            "last_name": "Suarez Miranda",
                            "email": "mock_user@amundsen.com",
                            "search_score": 61.40606,
                            "resource_type": "user",
                            "highlight": {},
                        }
                    ],
                    "total_results": 1,
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
                            "resource_type": "feature",
                            "highlight": {},
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
                            "resource_type": "feature",
                            "highlight": {},
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
                            "badges": ["pii"],
                            "search_score": 62.66787,
                            "resource_type": "feature",
                            "highlight": {},
                        },
                    ],
                    "total_results": 3,
                },
            },
            status_code=200,
        )

        self.assertEqual(actual, expected)

    def test_format_response_with_highlighting(self) -> None:
        responses = [
            Response(
                Search(using=self.mock_elasticsearch_client), ES_RESPONSE_HIGHLIGHTED
            )
        ]
        actual = create_search_response(
            page_index=0,
            results_per_page=1,
            responses=responses,
            resource_types=[Resource.TABLE],
            resource_to_field_mapping=ElasticsearchProxyV2_1.RESOURCE_TO_MAPPING,
        )
        expected = SearchResponse(
            msg="Success",
            page_index=0,
            results_per_page=1,
            results={
                "table": {
                    "results": [
                        {
                            "key": "mock_db://mock_cluster.mock_schema/mock_table_1",
                            "badges": ["pii", "beta"],
                            "tag": ["mock_tag_1", "mock_tag_2", "mock_tag_3"],
                            "schema": "mock_schema",
                            "table": "mock_table_1",
                            "column": ["mock_col_1", "mock_col_2", "mock_col_3"],
                            "database": "mock_db",
                            "cluster": "mock_cluster",
                            "description": "mock table description",
                            "resource_type": "table",
                            "search_score": 804.52716,
                            "highlight": {
                                "name": ["<em>mock</em>_table_1"],
                                "columns": [
                                    "<em>mock</em>_col_1",
                                    "<em>mock</em>_col_2",
                                    "<em>mock</em>_col_3",
                                ],
                                "description": ["<em>mock</em> table description"],
                            },
                        }
                    ],
                    "total_results": 2,
                }
            },
            status_code=200,
        )

        self.assertEqual(actual, expected)
