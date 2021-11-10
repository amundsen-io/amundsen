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

    def test_es_search_format_response(self) -> None:

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
        print(formatted_response)
        self.assertTrue(False)
