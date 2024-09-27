# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import unittest
from typing import Any, Dict

from mock import MagicMock, patch
from pyhocon import ConfigFactory
from datetime import datetime

from databuilder.extractor.redshift_table_last_updated_extractor import RedshiftTableLastUpdatedExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.table_last_updated import TableLastUpdated


class TestRedshiftTableLastUpdatedExtractor(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)

        config_dict = {
            f'extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}': 'TEST_CONNECTION',
            RedshiftTableLastUpdatedExtractor.CLUSTER_KEY: 'MY_CLUSTER',
            RedshiftTableLastUpdatedExtractor.USE_CATALOG_AS_CLUSTER_NAME: False,
            RedshiftTableLastUpdatedExtractor.DATABASE_KEY: 'redshift'
        }
        self.conf = ConfigFactory.from_dict(config_dict)

    def test_extraction_with_empty_query_result(self) -> None:
        """
        Test Extraction with empty result from query
        """
        with patch.object(SQLAlchemyExtractor, '_get_connection'):
            extractor = RedshiftTableLastUpdatedExtractor()
            extractor.init(self.conf)

            results = extractor.extract()
            self.assertEqual(results, None)

    def test_extraction_with_single_result(self) -> None:
        with patch.object(SQLAlchemyExtractor, '_get_connection') as mock_connection:
            connection = MagicMock()
            mock_connection.return_value = connection
            sql_execute = MagicMock()
            connection.execute = sql_execute
            table = {'schema': 'test_schema',
                     'name': 'test_table',
                     'description': 'a table for testing',
                     'cluster':
                         self.conf[RedshiftTableLastUpdatedExtractor.CLUSTER_KEY]
                     }

            sql_execute.return_value = [
                self._union({'table_name': 'test_table',
                            'last_updated_time': datetime.fromtimestamp(1656155938),
                            'schema': 'test_schema',
                            'cluster': 'MY_CLUSTER',
                    }, table)
            ]

            extractor = RedshiftTableLastUpdatedExtractor()
            extractor.init(self.conf)
            actual = extractor.extract()
            expected = TableLastUpdated(
                db='redshift',
                cluster='MY_CLUSTER',
                schema='test_schema',
                table_name='test_table',
                last_updated_time_epoch=1656155938
            )

            self.assertEqual(expected.__repr__(), actual.__repr__())
            self.assertIsNone(extractor.extract())

    def test_extraction_with_multiple_results(self) -> None:
        with patch.object(SQLAlchemyExtractor, '_get_connection') as mock_connection:
            connection = MagicMock()
            mock_connection.return_value = connection
            sql_execute = MagicMock()
            connection.execute = sql_execute
            table = {'schema': 'test_schema',
                     'name': 'test_table',
                     'description': 'a table for testing',
                     'cluster':
                         self.conf[RedshiftTableLastUpdatedExtractor.CLUSTER_KEY]
                     }

            sql_execute.return_value = [
                self._union({'table_name': 'test_table1',
                            'last_updated_time': datetime.fromtimestamp(1656155938),
                            'schema': 'test_schema',
                            'cluster': 'MY_CLUSTER',
                    }, table),
                    self._union({'table_name': 'test_table2',
                            'last_updated_time': datetime.fromtimestamp(1656000000),
                            'schema': 'test_schema',
                            'cluster': 'MY_CLUSTER',
                    }, table)
            ]

            extractor = RedshiftTableLastUpdatedExtractor()
            extractor.init(self.conf)
            actual1 = extractor.extract()
            expected1 = TableLastUpdated(
                db='redshift',
                cluster='MY_CLUSTER',
                schema='test_schema',
                table_name='test_table1',
                last_updated_time_epoch=1656155938
            )

            actual2 = extractor.extract()
            expected2 = TableLastUpdated(
                db='redshift',
                cluster='MY_CLUSTER',
                schema='test_schema',
                table_name='test_table2',
                last_updated_time_epoch=1656000000
            )

            self.assertEqual(expected1.__repr__(), actual1.__repr__())
            self.assertEqual(expected2.__repr__(), actual2.__repr__())
            self.assertIsNone(extractor.extract())

    def _union(self,
               target: Dict[Any, Any],
               extra: Dict[Any, Any]) -> Dict[Any, Any]:
        target.update(extra)
        return target


class TestRedshiftTableLastUpdatedExtractorWithWhereClause(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.where_clause_suffix = """
        where table_schema in ('public') and table_name = 'movies'
        """

        config_dict = {
            RedshiftTableLastUpdatedExtractor.WHERE_CLAUSE_SUFFIX_KEY: self.where_clause_suffix,
            f'extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}':
                'TEST_CONNECTION'
        }
        self.conf = ConfigFactory.from_dict(config_dict)

    def test_sql_statement(self) -> None:
        """
        Test Extraction with empty result from query
        """
        with patch.object(SQLAlchemyExtractor, '_get_connection'):
            extractor = RedshiftTableLastUpdatedExtractor()
            extractor.init(self.conf)
            self.assertTrue(self.where_clause_suffix in extractor.sql_stmt)


if __name__ == '__main__':
    unittest.main()
