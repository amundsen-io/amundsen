# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import unittest
import uuid

from mock import MagicMock, patch
from neo4j import GraphDatabase
from pyhocon import ConfigFactory

from databuilder.publisher.neo4j_csv_unwind_publisher import Neo4jCsvUnwindPublisher
from databuilder.publisher.publisher_config_constants import Neo4jCsvPublisherConfigs, PublisherConfigs

here = os.path.dirname(__file__)


class TestPublish(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self._resource_path = os.path.join(here, '../resources/csv_publisher')

    def test_publisher_write_exception(self) -> None:
        with patch.object(GraphDatabase, 'driver') as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value = mock_session

            mock_write_transaction = MagicMock(side_effect=Exception('Could not write'))
            mock_session.__enter__.return_value.write_transaction = mock_write_transaction

            publisher = Neo4jCsvUnwindPublisher()

            conf = ConfigFactory.from_dict(
                {Neo4jCsvPublisherConfigs.NEO4J_END_POINT_KEY: 'bolt://999.999.999.999:7687/',
                 PublisherConfigs.NODE_FILES_DIR: f'{self._resource_path}/nodes',
                 PublisherConfigs.RELATION_FILES_DIR: f'{self._resource_path}/relations',
                 Neo4jCsvPublisherConfigs.NEO4J_USER: 'neo4j_user',
                 Neo4jCsvPublisherConfigs.NEO4J_PASSWORD: 'neo4j_password',
                 PublisherConfigs.JOB_PUBLISH_TAG: str(uuid.uuid4())}
            )
            publisher.init(conf)

            with self.assertRaises(Exception):
                publisher.publish()

    def test_publisher(self) -> None:
        with patch.object(GraphDatabase, 'driver') as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value = mock_session

            mock_write_transaction = MagicMock()
            mock_session.__enter__.return_value.write_transaction = mock_write_transaction

            publisher = Neo4jCsvUnwindPublisher()

            conf = ConfigFactory.from_dict(
                {Neo4jCsvPublisherConfigs.NEO4J_END_POINT_KEY: 'bolt://999.999.999.999:7687/',
                 PublisherConfigs.NODE_FILES_DIR: f'{self._resource_path}/nodes',
                 PublisherConfigs.RELATION_FILES_DIR: f'{self._resource_path}/relations',
                 Neo4jCsvPublisherConfigs.NEO4J_USER: 'neo4j_user',
                 Neo4jCsvPublisherConfigs.NEO4J_PASSWORD: 'neo4j_password',
                 PublisherConfigs.JOB_PUBLISH_TAG: str(uuid.uuid4())}
            )
            publisher.init(conf)
            publisher.publish()

            # Create 2 indices, write 2 node files, write 1 relation file
            self.assertEqual(5, mock_write_transaction.call_count)


if __name__ == '__main__':
    unittest.main()
