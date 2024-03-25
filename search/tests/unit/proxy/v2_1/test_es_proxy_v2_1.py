# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock

from amundsen_common.models.search import Filter, HighlightOptions
from elasticsearch_dsl import Search

from search_service import create_app
from search_service.proxy.es_proxy_v2_1 import ElasticsearchProxyV2_1, Resource
from tests.unit.proxy.v2_1.fixtures_v2_1 import (
    FILTER_QUERY, TERM_FILTERS_QUERY, TERM_QUERY,
)


class TestElasticsearchProxyV2_1(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class="search_service.config.LocalConfig")
        self.app_context = self.app.app_context()
        self.app_context.push()
        mock_index = "mock_index"
        self.mock_elasticsearch_client = MagicMock()

        self.mock_elasticsearch_client.indices.get_alias.return_value = {mock_index: {}}
        self.mock_elasticsearch_client.indices.get_mapping.return_value = {
            mock_index: {"mappings": {"_meta": {"version": 2}}}
        }
        self.es_proxy = ElasticsearchProxyV2_1(
            host="mock_host",
            user="mock_user",
            password="mock_password",
            client=self.mock_elasticsearch_client,
            page_size=10,
        )

    def test_build_elasticsearch_query_term_filters(self) -> None:
        actual = self.es_proxy._build_elasticsearch_query(
            resource=Resource.FEATURE,
            query_term="mock_feature",
            filters=[
                Filter(name="badges", values=["pii"], operation="AND"),
                Filter(
                    name="feature_group",
                    values=["test_group", "mock_group"],
                    operation="OR",
                ),
            ],
        )
        expected = TERM_FILTERS_QUERY

        self.assertDictEqual(actual.to_dict(), expected)

    def test_build_elasticsearch_query_term_no_filters(self) -> None:
        actual = self.es_proxy._build_elasticsearch_query(
            resource=Resource.TABLE, query_term="mock_table", filters=[]
        )
        expected = TERM_QUERY

        self.assertDictEqual(actual.to_dict(), expected)

    def test_build_elasticsearch_query_just_filters(self) -> None:
        actual = self.es_proxy._build_elasticsearch_query(
            resource=Resource.DASHBOARD,
            query_term="",
            filters=[
                Filter(name="name", values=["mock_dashobard_*"], operation="OR"),
                Filter(
                    name="group_name",
                    values=["test_group", "mock_group"],
                    operation="OR",
                ),
                Filter(name="tag", values=["tag_*", "tag_2"], operation="AND"),
            ],
        )
        expected = FILTER_QUERY

        self.assertDictEqual(actual.to_dict(), expected)

    def test_search_highlight(self) -> None:
        self.maxDiff = None
        mock_es_dsl_search = Search()
        actual = self.es_proxy._search_highlight(
            resource=Resource.TABLE,
            search=mock_es_dsl_search,
            highlight_options={Resource.TABLE: HighlightOptions(enable_highlight=True)},
        ).to_dict()
        expected = {
            "highlight": {
                "fields": {
                    "name": {"type": "fvh", "number_of_fragments": 0},
                    "description": {
                        "type": "fvh",
                        "number_of_fragments": 0,
                    },
                    "columns.general": {
                        "type": "fvh",
                        "number_of_fragments": 10,
                        "order": "score",
                    },
                    "column_descriptions": {
                        "type": "fvh",
                        "number_of_fragments": 5,
                        "order": "score",
                    },
                }
            }
        }

        self.assertDictEqual(actual, expected)
