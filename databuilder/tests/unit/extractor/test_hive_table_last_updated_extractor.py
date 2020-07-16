# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import unittest
from datetime import datetime
from pytz import UTC

from mock import patch, MagicMock
from pyhocon import ConfigFactory
from typing import Any, Dict  # noqa: F401

from databuilder.extractor.hive_table_last_updated_extractor import HiveTableLastUpdatedExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.table_last_updated import TableLastUpdated
from databuilder.filesystem.filesystem import FileSystem
from databuilder.filesystem.metadata import FileMetadata


class TestHiveTableLastUpdatedExtractor(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        logging.basicConfig(level=logging.INFO)

    def test_extraction_with_empty_query_result(self):
        # type: () -> None

        config_dict = {
            'extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING):
                'TEST_CONNECTION',
            'filesystem.{}'.format(FileSystem.DASK_FILE_SYSTEM): MagicMock()
        }
        conf = ConfigFactory.from_dict(config_dict)
        with patch.object(SQLAlchemyExtractor, '_get_connection'):
            extractor = HiveTableLastUpdatedExtractor()
            extractor.init(conf)

            result = extractor.extract()
            self.assertEqual(result, None)

    def test_extraction_with_partition_table_result(self):
        # type: () -> None
        config_dict = {
            'filesystem.{}'.format(FileSystem.DASK_FILE_SYSTEM): MagicMock()
        }
        conf = ConfigFactory.from_dict(config_dict)

        pt_alchemy_extractor_instance = MagicMock()
        non_pt_alchemy_extractor_instance = MagicMock()
        with patch.object(HiveTableLastUpdatedExtractor, '_get_partitioned_table_sql_alchemy_extractor',
                          return_value=pt_alchemy_extractor_instance),\
            patch.object(HiveTableLastUpdatedExtractor, '_get_non_partitioned_table_sql_alchemy_extractor',
                         return_value=non_pt_alchemy_extractor_instance):
            pt_alchemy_extractor_instance.extract = MagicMock(side_effect=[
                {'schema': 'foo_schema',
                 'table_name': 'table_1',
                 'last_updated_time': 1},
                {'schema': 'foo_schema',
                 'table_name': 'table_2',
                 'last_updated_time': 2}
            ])

            non_pt_alchemy_extractor_instance.extract = MagicMock(return_value=None)

            extractor = HiveTableLastUpdatedExtractor()
            extractor.init(conf)

            result = extractor.extract()
            expected = TableLastUpdated(schema='foo_schema', table_name='table_1', last_updated_time_epoch=1,
                                        db='hive', cluster='gold')
            self.assertEqual(result.__repr__(), expected.__repr__())
            result = extractor.extract()
            expected = TableLastUpdated(schema='foo_schema', table_name='table_2', last_updated_time_epoch=2,
                                        db='hive', cluster='gold')
            self.assertEqual(result.__repr__(), expected.__repr__())

            self.assertIsNone(extractor.extract())

    def test_extraction(self):
        # type: () -> None
        old_datetime = datetime(2018, 8, 14, 4, 12, 3, tzinfo=UTC)
        new_datetime = datetime(2018, 11, 14, 4, 12, 3, tzinfo=UTC)

        fs = MagicMock()
        fs.ls = MagicMock(return_value=['/foo/bar', '/foo/baz'])
        fs.is_file = MagicMock(return_value=True)
        fs.info = MagicMock(side_effect=[
            FileMetadata(path='/foo/bar', last_updated=old_datetime, size=15093),
            FileMetadata(path='/foo/baz', last_updated=new_datetime, size=15094)
        ])

        pt_alchemy_extractor_instance = MagicMock()
        non_pt_alchemy_extractor_instance = MagicMock()

        with patch.object(HiveTableLastUpdatedExtractor,
                          '_get_partitioned_table_sql_alchemy_extractor', return_value=pt_alchemy_extractor_instance), \
            patch.object(HiveTableLastUpdatedExtractor,
                         '_get_non_partitioned_table_sql_alchemy_extractor',
                         return_value=non_pt_alchemy_extractor_instance), \
            patch.object(HiveTableLastUpdatedExtractor,
                         '_get_filesystem', return_value=fs):
            pt_alchemy_extractor_instance.extract = MagicMock(return_value=None)

            non_pt_alchemy_extractor_instance.extract = MagicMock(side_effect=[
                {'schema': 'foo_schema',
                 'table_name': 'table_1',
                 'location': '/foo/bar'}
            ])

            extractor = HiveTableLastUpdatedExtractor()
            extractor.init(ConfigFactory.from_dict({}))

            result = extractor.extract()
            expected = TableLastUpdated(schema='foo_schema', table_name='table_1',
                                        last_updated_time_epoch=1542168723,
                                        db='hive', cluster='gold')
            self.assertEqual(result.__repr__(), expected.__repr__())

            self.assertIsNone(extractor.extract())


if __name__ == '__main__':
    unittest.main()
