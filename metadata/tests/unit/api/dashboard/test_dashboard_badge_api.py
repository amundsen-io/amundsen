# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from http import HTTPStatus

from unittest.mock import patch, Mock

from tests.unit.test_basics import BasicTestCase
from metadata_service.entity.badge import Badge

DASHBOARD_NAME = 'magic'
BADGE_NAME = 'alpha'


class TestDashboardBadgeAPI(BasicTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.mock_client = patch('metadata_service.api.dashboard.get_proxy_client')
        self.mock_proxy = self.mock_client.start().return_value = Mock()

    def tearDown(self) -> None:
        super().tearDown()

        self.mock_client.stop()

    def test_block_bad_badge_name(self) -> None:
        self.app.config['WHITELIST_BADGES'] = []
        response = self.app.test_client().put(f'/dashboard/{DASHBOARD_NAME}/badge/{BADGE_NAME}?category=table_status')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_block_badge_missing_category(self) -> None:
        self.app.config['WHITELIST_BADGES'] = [Badge(badge_name='alpha',
                                                     category='table_status')]
        response = self.app.test_client().put(f'/dashboard/{DASHBOARD_NAME}/badge/{BADGE_NAME}')

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_badge_with_category(self) -> None:
        self.app.config['WHITELIST_BADGES'] = [Badge(badge_name='alpha',
                                                     category='table_status')]
        response = self.app.test_client().put(f'/dashboard/{DASHBOARD_NAME}/badge/{BADGE_NAME}?category=table_status')

        self.assertEqual(response.status_code, HTTPStatus.OK)


if __name__ == '__main__':
    unittest.main()
