# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import unittest
from http import HTTPStatus
from unittest.mock import Mock, patch

import responses
from amundsen_common.models.search import Filter

from amundsen_application import create_app
from amundsen_application.api.search.v1 import SEARCH_ENDPOINT, _transform_filters

local_app = create_app('amundsen_application.config.TestConfig', 'tests/templates')

MOCK_TABLE_RESULTS = {
    "results": [
        {
            "key": "test_key",
            "badges": [],
            "tag": [],
            "schema": "test_schema",
            "table": "test_table",
            "description": "mock description",
            "column": [
                "column_1",
                "column_2",
                "column_3"
            ],
            "database": "test_db",
            "cluster": "test_cluster",
            "search_score": 0.0
        }
    ],
    "total_results": 1
}

MOCK_PARSED_TABLE_RESULTS = [
    {
        "key": "test_key",
        "badges": [],
        "tag": [],
        "schema": "test_schema",
        "table": "test_table",
        "description": "mock description",
        "column": [
            "column_1",
            "column_2",
            "column_3"
        ],
        "database": "test_db",
        "cluster": "test_cluster",
        "search_score": 0.0
    }
]


class Search(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_table_results = MOCK_TABLE_RESULTS
        self.expected_parsed_table_results = MOCK_PARSED_TABLE_RESULTS
        self.search_service_url = local_app.config['SEARCHSERVICE_BASE'] + SEARCH_ENDPOINT
        self.fe_flask_endpoint = '/api/search/v1/search'

    def test_fail_if_term_is_none(self) -> None:
        """
        Test request failure if 'term' is not provided in the request json
        :return:
        """
        with local_app.test_client() as test:
            response = test.post(self.fe_flask_endpoint, json={
                'pageIndex': 0,
                'filters': [],
                'resultsPerPage': 10,
                "highlight_options": {},
            })
            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    def test_fail_if_page_index_is_none(self) -> None:
        """
        Test request failure if 'pageIndex' is not provided in the request json
        :return:
        """
        with local_app.test_client() as test:
            response = test.post(self.fe_flask_endpoint, json={
                'term': 'test_term',
                'filters': [],
                'resultsPerPage': 10,
                "highlight_options": {},
            })
            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    def test_fail_if_results_per_page_is_none(self) -> None:
        """
        Test request failure if 'resultsPerPage' is not provided in the request json
        :return:
        """
        with local_app.test_client() as test:
            response = test.post(self.fe_flask_endpoint, json={
                'term': 'test_term',
                'pageIndex': 0,
                'filters': [],
                "highlight_options": {},
            })
            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    def test_transform_filters(self) -> None:
        test_filters = {
            "table": {
                "schema": {
                    "value": "test_schema",
                    "operation": "OR"
                }
            }
        }
        test_resources = ['table']
        actual = _transform_filters(filters=test_filters, resources=test_resources)
        expected = [Filter(name='schema',
                           values=['test_schema'],
                           operation='OR')]
        self.assertEqual(actual, expected)

    @responses.activate
    @patch('amundsen_application.api.search.v1._transform_filters')
    def test_calls_transform_filters(self, transform_filter_mock: Mock) -> None:
        """
        Test transform_filters is called with the filters from the request json
        from the request_json
        :return:
        """
        test_term = 'hello'
        test_index = 1
        test_results_per_page = 10
        test_resources = ['table']
        test_filters = {
            "table": {
                "schema": {
                    "value": "test_schema",
                    "operation": "OR"
                }
            }
        }
        responses.add(responses.POST,
                      self.search_service_url,
                      json=self.mock_table_results,
                      status=HTTPStatus.OK)

        with local_app.test_client() as test:
            test.post(self.fe_flask_endpoint,
                      json={
                          "searchTerm": test_term,
                          "pageIndex": test_index,
                          "resultsPerPage": test_results_per_page,
                          "resources": test_resources,
                          "filters": test_filters,
                          "highlight_options": {},
                      })
            transform_filter_mock.assert_called_with(filters=test_filters, resources=test_resources)

    @responses.activate
    @patch('amundsen_application.api.search.v1._transform_filters')
    @patch('amundsen_application.api.search.v1.generate_query_request')
    def test_calls_generate_query_request(self,
                                          mock_generate_query_request: Mock,
                                          transform_filter_mock: Mock) -> None:
        """
        Test generate_query_json helper method is called with correct arguments
        from the request_json if filters exist
        :return:
        """
        test_term = 'hello'
        test_index = 1
        test_results_per_page = 10
        test_resources = ['table']
        test_filters = {
            "table": {
                "schema": {
                    "value": "test_schema",
                    "operation": "OR"
                }
            }
        }
        responses.add(responses.POST,
                      self.search_service_url,
                      json=self.mock_table_results,
                      status=HTTPStatus.OK)
        mock_filters = [Filter(name='schema',
                               values=['test_schema'],
                               operation='OR')]
        transform_filter_mock.return_value = mock_filters

        with local_app.test_client() as test:
            test.post(self.fe_flask_endpoint,
                      json={
                          "searchTerm": test_term,
                          "pageIndex": test_index,
                          "resultsPerPage": test_results_per_page,
                          "resources": test_resources,
                          "filters": test_filters,
                          "highlight_options": {},
                      })
            mock_generate_query_request.assert_called_with(filters=mock_filters,
                                                           resources=test_resources,
                                                           page_index=test_index,
                                                           results_per_page=test_results_per_page,
                                                           search_term=test_term,
                                                           highlight_options={})

    @responses.activate
    @patch('amundsen_application.api.search.v1._search_resources')
    def test_request_success(self, search_resources_mock: Mock) -> None:
        """
        Test that the response contains the expected data and status code on success
        :return:
        """
        test_term = 'hello'
        test_index = 1
        test_results_per_page = 10
        test_resources = ['table']
        test_filters = {
            "table": {
                "schema": {
                    "value": "test_schema",
                    "operation": "OR"
                }
            }
        }
        responses.add(responses.POST,
                      self.search_service_url,
                      json=self.mock_table_results,
                      status=HTTPStatus.OK)

        search_resources_mock.return_value = {
            "search_term": test_term,
            "msg": "Success",
            "table": self.mock_table_results,
            "dashboard": {},
            "feature": {},
            "user": {},
            "status_code": HTTPStatus.OK
        }

        with local_app.test_client() as test:
            response = test.post(self.fe_flask_endpoint,
                                 json={
                                     "searchTerm": test_term,
                                     "pageIndex": test_index,
                                     "resultsPerPage": test_results_per_page,
                                     "resources": test_resources,
                                     "filters": test_filters,
                                     "highlight_options": {},
                                 })
            data = json.loads(response.data)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            results = data['table']
            self.assertEqual(results['total_results'], self.mock_table_results['total_results'])
            self.assertEqual(results['results'], self.expected_parsed_table_results)

    @responses.activate
    @patch('amundsen_application.api.search.v1._search_resources')
    def test_request_fail(self, search_resources_mock: Mock) -> None:
        """
        Test that the response containes the failure status code from the search service on failure
        :return:
        """
        test_term = 'hello'
        test_index = 1
        test_results_per_page = 10
        test_resources = ['table']
        test_filters = {
            "schema": {
                "value": "test_schema",
                "operation": "OR"
            }
        }
        responses.add(responses.POST, self.search_service_url, json={}, status=HTTPStatus.BAD_REQUEST)
        search_resources_mock.return_value = {
            "search_term": test_term,
            "msg": "Invalid search response",
            "table": {},
            "dashboard": {},
            "feature": {},
            "user": {},
            "status_code": HTTPStatus.BAD_REQUEST
        }
        with local_app.test_client() as test:
            response = test.post(self.fe_flask_endpoint,
                                 json={
                                     "searchTerm": test_term,
                                     "pageIndex": test_index,
                                     "resultsPerPage": test_results_per_page,
                                     "resources": test_resources,
                                     "filters": test_filters,
                                     "highlight_options": {},
                                 })
            data = json.loads(response.data)

            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(data['msg'], 'Invalid search response')
