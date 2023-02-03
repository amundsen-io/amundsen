# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

# TODO temp imports fixer /
import sys

sys.path.append('/Users/bdye/src/amundsenfrontend-private/upstream/frontend')

# /TODO temp imports fixer

import unittest
from http import HTTPStatus

from flask import Response

from amundsen_application import create_app
from amundsen_application.api.notice import v0

local_app = create_app('amundsen_application.config.TestConfig', 'tests/templates')
NOTICE_CLIENT_CLASS = ('amundsen_application.base.examples.example_notice_client.NoticeClient')  # TODO implement

class NoticeTest(unittest.TestCase):

    def setUp(self) -> None:
        pass
    
    def test_no_client_class(self) -> None:
        """
        Test that the expected not-implemented response is returned when ALERT_CLIENT is None
        :return:
        """
        # Reset side effects of other tests to ensure results are same regardless of execution order.
        v0.NOTICE_CLIENT_INSTANCE = None

        local_app.config['NOTICE_CLIENT'] = None

        with local_app.test_client() as test:
            response = test.get('/api/notice/v0/table/summary')
            self.assertEqual(response.status_code, HTTPStatus.NOT_IMPLEMENTED)
    
    @unittest.mock.patch(NOTICE_CLIENT_CLASS + '._get_table_notices_summary')
    def test_good_client_response(self, mock_get_table_notices_summary: unittest.mock.Mock) -> None:
        local_app.config['NOTICE_CLIENT'] = NOTICE_CLIENT_CLASS
        mock_get_table_notices_summary.return_value = Response(response='',
                                               status=HTTPStatus.OK)
        with local_app.test_client() as test:
            response = test.get('api/notice/v0/table/summary')
            self.assertEqual(response.status_code, HTTPStatus.OK)    

if __name__ == '__main__':
    unittest.main()