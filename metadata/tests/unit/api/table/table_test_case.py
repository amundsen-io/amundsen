# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from mock import patch, Mock

from tests.unit.test_basics import BasicTestCase


class TableTestCase(BasicTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.mock_client = patch('metadata_service.api.table.get_proxy_client')
        self.mock_proxy = self.mock_client.start().return_value = Mock()

    def tearDown(self):
        super().tearDown()
        self.mock_client.stop()
