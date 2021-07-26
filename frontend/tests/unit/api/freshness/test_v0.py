# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
import json
from flask import make_response, jsonify
from http import HTTPStatus
from typing import Dict

from flask import Response

from amundsen_application import create_app
from amundsen_application.api.freshness import v0
from amundsen_application.base.base_data_freshness_client import BaseDataFreshnessClient

local_app = create_app('amundsen_application.config.TestConfig', 'tests/templates')
DATA_FRESHNESS_CLIENT = 'tests.unit.api.freshness.test_v0.DataFreshnessClient'


class DataFreshnessClient(BaseDataFreshnessClient):
    def __init__(self) -> None:
        pass

    def get_freshness_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        return make_response(jsonify({
            'freshness_data': {'columns': [{}], 'data': [{'latest updated_at': '2021-07-14 13:52:51.807 +0000'}]}
        }), HTTPStatus.OK)


class DataFreshnessTest(unittest.TestCase):

    def setUp(self) -> None:
        local_app.config['DATA_FRESHNESS_CLIENT_ENABLED'] = True

    def test_no_client_class(self) -> None:
        """
        Test that Not Implemented error is raised when FRESHNESS_CLIENT is None
        :return:
        """
        # Reset side effects of other tests to ensure that the results are the
        # same regardless of execution order
        v0.DATA_FRESHNESS_CLIENT_CLASS = None
        v0.DATA_FRESHNESS_CLIENT_INSTANCE = None

        local_app.config['DATA_FRESHNESS_CLIENT'] = None
        with local_app.test_client() as test:
            response = test.post('/api/freshness/v0/')
            self.assertEqual(response.status_code, HTTPStatus.NOT_IMPLEMENTED)

    @unittest.mock.patch('amundsen_application.api.freshness.v0._get_table_metadata')
    def test_client_response(self, mock_get_table_metadata: unittest.mock.Mock) -> None:
        """
        Test response
        """
        mock_get_table_metadata.return_value = {}

        local_app.config['DATA_FRESHNESS_CLIENT'] = DATA_FRESHNESS_CLIENT

        expected_response_json = {
            'freshnessData': {
                'columns': [{}],
                'data': [{'latest updated_at': '2021-07-14 13:52:51.807 +0000'}]}
        }

        with local_app.test_client() as test:
            request_data = {
                'database': 'fake_db',
                'cluster': 'fake_cluster',
                'schema': 'fake_schema',
                'tableName': 'fake_table'
            }
            post_response = test.post('/api/freshness/v0/',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            self.assertEqual(post_response.status_code, HTTPStatus.OK)
            self.assertEqual(post_response.json, expected_response_json)
