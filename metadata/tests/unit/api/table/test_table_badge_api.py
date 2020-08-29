# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from http import HTTPStatus

from unittest.mock import patch, Mock

from tests.unit.test_basics import BasicTestCase

TABLE_NAME = 'magic'
BADGE_NAME = 'foo'
TAG_NAME = 'bar'


class TableTagAPI(BasicTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.mock_client = patch('metadata_service.api.table.get_proxy_client')
        self.mock_proxy = self.mock_client.start().return_value = Mock()

    def tearDown(self):
        super().tearDown()

        self.mock_client.stop()

    def test_block_tag_on_reserved_badge_value(self) -> None:
        self.app.config['WHITELIST_BADGES'] = [BADGE_NAME]
        response = self.app.test_client().put(f'/table/{TABLE_NAME}/tag/{BADGE_NAME}')

        self.assertEqual(response.status_code, HTTPStatus.CONFLICT)

    def test_tag_on_unreserved_badge_value(self) -> None:
        self.app.config['WHITELIST_BADGES'] = [BADGE_NAME]
        response = self.app.test_client().put(f'/table/{TABLE_NAME}/tag/{TAG_NAME}')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_badge_on_reserved_badge_value(self) -> None:
        self.app.config['WHITELIST_BADGES'] = [BADGE_NAME]
        response = self.app.test_client().put(f'/table/{TABLE_NAME}/tag/{BADGE_NAME}?tag_type=badge')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_badge_on_unreserved_badge_value(self) -> None:
        self.app.config['WHITELIST_BADGES'] = [BADGE_NAME]
        response = self.app.test_client().put(f'/table/{TABLE_NAME}/tag/{TAG_NAME}?tag_type=badge')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


if __name__ == '__main__':
    unittest.main()
