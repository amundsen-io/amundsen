# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import unittest

from mock import MagicMock, patch
from pyhocon import ConfigFactory

from databuilder.publisher import nebula_csv_publisher
from databuilder.publisher.nebula_csv_publisher import NebulaCsvPublisher

here = os.path.dirname(__file__)


class TestPublish(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)
        resource_path = os.path.join(here, '../resources/nebula_csv_publisher')
        self.conf = ConfigFactory.from_dict({
        nebula_csv_publisher.VERTEX_FILES_DIR: f'{resource_path}/nodes',
        nebula_csv_publisher.EDGE_FILES_DIR: f'{resource_path}/relations',
        nebula_csv_publisher.NEBULA_ENDPOINTS: "test:9669",
        nebula_csv_publisher.NEBULA_USER: "test_user",
        nebula_csv_publisher.NEBULA_PASSWORD: "test_password",
        nebula_csv_publisher.JOB_PUBLISH_TAG: "test_tag",
    })

    @patch.object(nebula_csv_publisher, 'NebulaConfig')
    @patch.object(nebula_csv_publisher, 'ConnectionPool')
    def test_publisher(self, mock_cp, mock_config) -> None:
        mock_conn_pool = MagicMock()
        mock_cp.return_value = mock_conn_pool

        mock_config.return_value = MagicMock()

        mock_conn_pool.init.return_value = None

        mock_session_context = MagicMock()
        mock_conn_pool.session_context.return_value.__enter__.return_value = mock_session_context

        mock_session_execute = MagicMock()
        mock_session_context.execute = mock_session_execute

        publisher = NebulaCsvPublisher()
        publisher.init(conf=self.conf)
        publisher.publish()

        self.assertEqual(13, mock_session_execute.call_count)


if __name__ == '__main__':
    unittest.main()
