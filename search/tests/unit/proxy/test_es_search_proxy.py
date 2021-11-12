# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
import json
from typing import (  # noqa: F401
    Any, Iterable, List, Dict
)
from unittest import mock
from unittest.mock import MagicMock, patch

from elasticsearch_dsl import Search
from elasticsearch_dsl.response import Response

from search_service import create_app
from search_service.proxy.es_search_proxy import ElasticsearchProxy, Resource
from search_service.proxy.es_search_proxy import Filter
from tests.unit.proxy.fixtures import TERM_FILTERS_QUERY, TERM_QUERY, FILTER_QUERY

class TestElasticsearchProxy(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

        mock_elasticsearch_client = MagicMock()
        self.es_proxy = ElasticsearchProxy(client=mock_elasticsearch_client)

    def test_es_search_request(self) -> None:
        self.es_proxy.search(query_term="rides",
                             page_index=0,
                             results_per_page=10,
                             resource_types=[],
                             filters=[
                                 Filter(name='badges', values=['ga', 'co*'], operation='OR'),
                                 Filter(name='column', values=['ds', 'ride_id'], operation='AND')
                             ])
        self.assertTrue(False)

    def test_build_elasticsearch_query_term_filters(self) -> None:
        # TODO check how they implement equality for query objects and not convert to dict
        actual = self.es_proxy._build_elasticsearch_query(resource=Resource.FEATURE,
                                                 query_term="mock_feature",
                                                 filters=[
                                                     Filter(name='badges', values=['pii'], operation='AND'),
                                                     Filter(name='feature_group', values=['test_group', 'mock_group'], operation='OR')
                                                     ])
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
                                                              Filter(name='name', values=['mock_dashobard_*'], operation='OR'),
                                                              Filter(name='group_name', values=['test_group', 'mock_group'], operation='OR'),
                                                              Filter(name='tag', values=['tag_*', 'tag_2'], operation='AND')
                                                          ])
        expected = FILTER_QUERY
        self.assertDictEqual(actual.to_dict(), expected)

    def test_es_search_format_response(self) -> None:
        # TODO take 3 different responses 
        mock_es_dsl_search = Search()
        json_responses = []
        import os
        with open(f'{os.path.dirname(__file__)}/data/sample_response.json') as json_resp:
            json_responses = json.load(json_resp)['responses']
        mock_es_dsl_responses = [Response(mock_es_dsl_search, r) for r in json_responses]
        formatted_response = self.es_proxy._format_response(page_index=0,
                                                            results_per_page=10,
                                                            responses=mock_es_dsl_responses,
                                                            resource_types=[Resource.TABLE, Resource.USER])
        print(json.dumps(formatted_response))
        self.assertTrue(False)
