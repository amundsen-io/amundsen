# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from typing import Any

from mock import MagicMock, patch
from pyhocon import ConfigFactory

from databuilder import Scoped
from databuilder.extractor import nebula_extractor
from databuilder.extractor.nebula_extractor import NebulaExtractor
from databuilder.models.table_elasticsearch_document import TableESDocument


class TestNebulaExtractor(unittest.TestCase):

    def setUp(self) -> None:
        config_dict = {
            f'extractor.nebula.{NebulaExtractor.GRAPH_URL_CONFIG_KEY}':
            'TEST_GRAPH_URL',
            f'extractor.nebula.{NebulaExtractor.CYPHER_QUERY_CONFIG_KEY}':
            'TEST_QUERY',
            f'extractor.nebula.{NebulaExtractor.NEBULA_AUTH_USER}':
            'TEST_USER',
            f'extractor.nebula.{NebulaExtractor.NEBULA_AUTH_PW}': 'TEST_PW',
            f'extractor.nebula.{NebulaExtractor.NEBULA_ENDPOINTS}':
            'test:9669',
        }

        self.conf = ConfigFactory.from_dict(config_dict)

    @patch.object(NebulaExtractor, '_execute_query')
    @patch.object(nebula_extractor, 'NebulaConfig')
    @patch.object(nebula_extractor, 'ConnectionPool')
    def test_extraction_with_model_class(self: Any, conn_pool_mock: Any,
                                         nebula_config_mock: Any,
                                         execute_query_mock: Any) -> None:
        """
        Test Extraction using model class
        """
        mock_conn_pool = MagicMock()
        conn_pool_mock.return_value = mock_conn_pool

        nebula_config_mock.return_value = MagicMock()

        mock_conn_pool.init.return_value = None

        mock_session_context = MagicMock()
        mock_conn_pool.session_context.return_value.__enter__.return_value = mock_session_context

        config_dict = {
            f'extractor.nebula.{NebulaExtractor.GRAPH_URL_CONFIG_KEY}':
            'TEST_GRAPH_URL',
            f'extractor.nebula.{NebulaExtractor.CYPHER_QUERY_CONFIG_KEY}':
            'TEST_QUERY',
            f'extractor.nebula.{NebulaExtractor.NEBULA_AUTH_USER}':
            'TEST_USER',
            f'extractor.nebula.{NebulaExtractor.NEBULA_AUTH_PW}': 'TEST_PW',
            f'extractor.nebula.{NebulaExtractor.MODEL_CLASS_CONFIG_KEY}':
            'databuilder.models.table_elasticsearch_document.TableESDocument',
            f'extractor.nebula.{NebulaExtractor.NEBULA_ENDPOINTS}': 'test:9669'
        }

        self.conf = ConfigFactory.from_dict(config_dict)

        extractor = NebulaExtractor()

        extractor.init(
            Scoped.get_scoped_conf(conf=self.conf,
                                   scope=extractor.get_scope()))

        results = [{
            'spaceName':
            'amundsen',
            'data': [{
                'meta': [
                    None, None, None, None, None, None, None, None,
                    [None, None, None, None, None],
                    [None, None, None, None, None], None, None,
                    [None, None, None, None], [{
                        'type': 'vertex',
                        'id': 'beta'
                    }], [None, None]
                ],
                'row': [
                    'test_database', 'test_cluster', 'test_schema',
                    'schema_description', 'test_table_name',
                    'test_database://test_cluster.test_schema/test_table_name',
                    'test_table_description', 123456789,
                    ['test_col1', 'test_col2', 'test_col3'],
                    ['test_description1', 'test_description2', ''], 100, 5,
                    ['test_database'], ['badge1'], ['TEST']
                ]
            }],
            'columns': [
                'database', 'cluster', 'schema', 'schema_description', 'name',
                'key', 'description', 'last_updated_timestamp', 'column_names',
                'column_descriptions', 'total_usage', 'unique_usage', 'tags',
                'badges', 'programmatic_descriptions'
            ],
            'errors': {
                'code': 0
            },
            'latencyInUs':
            9854
        }]

        execute_query_mock.return_value = results

        result_obj = extractor.extract()

        result_dict = dict(
            database='test_database',
            cluster='test_cluster',
            schema='test_schema',
            name='test_table_name',
            display_name='test_schema.test_table_name',
            key='test_database://test_cluster.test_schema/test_table_name',
            description='test_table_description',
            last_updated_timestamp=123456789,
            column_names=['test_col1', 'test_col2', 'test_col3'],
            column_descriptions=['test_description1', 'test_description2', ''],
            total_usage=100,
            unique_usage=5,
            tags=['test_database'],
            badges=['badge1'],
            schema_description='schema_description',
            programmatic_descriptions=['TEST'])

        self.assertIsInstance(result_obj, TableESDocument)
        self.assertDictEqual(vars(result_obj), result_dict)


if __name__ == '__main__':
    unittest.main()
