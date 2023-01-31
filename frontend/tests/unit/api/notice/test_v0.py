# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from http import HTTPStatus

from flask import Response

from amundsen_application import create_app
from amundsen_application.api.notice import v0

class NoticeTest(unittest.TestCase):

    def setUp(self) -> None:
        pass
    
    def test_no_client_class(self) -> None:
        """
        Test that the expected not-implemented response is returned when ALERT_CLIENT is None
        :return:
        """
        # Reset side effects of other tests to ensure results are same regardless of execution order.
        v0.ALERT_CLIENT_INSTANCE = None