# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from amundsen_application.base.base_notice_client import BaseNoticeClient
from amundsen_application.api.notice import v0
from amundsen_application import create_app
from flask import Response
from http import HTTPStatus
import unittest

local_app = create_app('amundsen_application.config.TestConfig', 'tests/templates')


class DummyNoticeClient(BaseNoticeClient):

    def get_table_notices_summary(self, *, table_key: str) -> Response:
        pass


dummy_notice_client_class = 'tests.unit.api.notice.test_v0.DummyNoticeClient'


class NoticeTest(unittest.TestCase):

    def setUp(self) -> None:
        local_app.config['NOTICE_CLIENT_ENABLED'] = True

    def test_no_client_class(self) -> None:
        """
        Test that the expected not-implemented response is returned when NOTICE_CLIENT is None
        :return:
        """
        # Reset side effects of other tests to ensure results are same regardless of execution order.
        v0.NOTICE_CLIENT_INSTANCE = None

        local_app.config['NOTICE_CLIENT'] = None

        with local_app.test_client() as test:
            response = test.get('/api/notices/v0/table?key=some_table_key')
            self.assertEqual(response.status_code, HTTPStatus.NOT_IMPLEMENTED)
            self.assertEqual(
                response.json, {'notices': {}, 'msg': 'A client for retrieving resource notices must be configured'})

    @unittest.mock.patch(dummy_notice_client_class + '.get_table_notices_summary')
    def test_good_client_response(self, mock_get_table_notices_summary: unittest.mock.Mock) -> None:
        local_app.config['NOTICE_CLIENT'] = dummy_notice_client_class
        mock_get_table_notices_summary.return_value = Response(response='',
                                                               status=HTTPStatus.OK)
        with local_app.test_client() as test:
            response = test.get('api/notice/v0/table/summary')
            self.assertEqual(response.status_code, HTTPStatus.OK)
