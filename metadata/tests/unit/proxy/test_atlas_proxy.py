import unittest

from atlasclient.exceptions import BadRequest
from mock import patch, MagicMock

from metadata_service.entity.popular_table import PopularTable
from metadata_service.entity.table_detail import (Table)
from metadata_service.exception import NotFoundException
from metadata_service.proxy.atlas_proxy import AtlasProxy


class TestAtlasProxy(unittest.TestCase):

    def setUp(self):
        with patch('metadata_service.proxy.atlas_proxy.Atlas'):
            self.proxy = AtlasProxy(host='DOES_NOT_MATTER', port=0000)
            self.proxy._driver = MagicMock()

        self.db = 'TEST_DB'
        self.cluster = 'TEST_CLUSTER'
        self.schema = 'TEST_SCHEMA'
        self.name = 'TEST_TABLE'
        self.table_uri = f'{self.db}://{self.cluster}.{self.schema}/{self.name}'

        entity1_relationships = {
            'relationshipAttributes': {
                'columns': []
            }
        }
        self.entity1 = {
            'guid': '1',
            'updateTime': 123,
            'attributes': {
                'qualifiedName': 'Table1_Qualified',
                'schema': self.schema,
                'name': 'Table1',
                'db': {
                    'guid': '-100',
                    'qualifiedName': self.db
                }
            }
        }
        self.entity1.update(entity1_relationships)
        self.entity1['attributes'].update(entity1_relationships)

        entity2_relationships = {
            'relationshipAttributes': {
                'columns': []
            }
        }
        self.entity2 = {
            'guid': '2',
            'updateTime': 234,
            'attributes': {
                'qualifiedName': 'Table2_Qualified',
                'schema': self.schema,
                'name': 'Table1',
                'db': {
                    'guid': '-100',
                    'qualifiedName': self.db
                }
            }
        }
        self.entity2.update(entity2_relationships)
        self.entity2['attributes'].update(entity2_relationships)

        self.entities = {
            'entities': [
                self.entity1,
                self.entity2,
            ]
        }

    def test_extract_table_uri_info(self):
        table_info = self.proxy._extract_info_from_uri(table_uri=self.table_uri)
        self.assertDictEqual(table_info, {
            'db': self.db,
            'cluster': self.cluster,
            'schema': self.schema,
            'name': self.name
        })

    def test_get_ids_from_basic_search(self):
        basic_search_response = MagicMock()
        basic_search_response._data = self.entities

        self.proxy._driver.search_basic = MagicMock(return_value=[basic_search_response])
        response = self.proxy._get_ids_from_basic_search(params={})
        expected = ['1', '2']
        self.assertListEqual(response, expected)

    def test_get_table(self):
        unique_attr_response = MagicMock()
        unique_attr_response.entity = self.entity1

        self.proxy._driver.entity_unique_attribute = MagicMock(return_value=unique_attr_response)
        response = self.proxy.get_table(table_uri=self.table_uri)

        expected = Table(database=self.db,
                         cluster=self.cluster,
                         schema=self.schema,
                         name=self.name,
                         columns=self.entity1['relationshipAttributes']['columns'],
                         last_updated_timestamp=self.entity1['updateTime'])
        self.assertEqual(str(expected), str(response))

    def test_get_table_not_found(self):
        with self.assertRaises(NotFoundException):
            self.proxy._driver.entity_unique_attribute = MagicMock(side_effect=Exception('Boom!'))
            self.proxy.get_table(table_uri=self.table_uri)

    def test_get_table_missing_info(self):
        with self.assertRaises(BadRequest):
            local_entity = self.entity1
            local_entity.pop('relationshipAttributes')
            unique_attr_response = MagicMock()
            unique_attr_response.entity = local_entity

            self.proxy._driver.entity_unique_attribute = MagicMock(return_value=unique_attr_response)
            self.proxy.get_table(table_uri=self.table_uri)

    @patch.object(AtlasProxy, '_get_ids_from_basic_search')
    def test_get_popular_tables(self, mock_basic_search):
        entity1 = MagicMock()
        entity1.attributes = self.entity1['attributes']

        entity2 = MagicMock()
        entity2.attributes = self.entity2['attributes']

        bulk_ent_collection = MagicMock()
        bulk_ent_collection.entities = [entity1, entity2]

        self.proxy._driver.entity_bulk = MagicMock(return_value=[bulk_ent_collection])

        db_entity = MagicMock()
        db_entity.entity = {'attributes': {
            'qualifiedName': self.db,
            'cluster': self.cluster
        }}

        self.proxy._driver.entity_guid = MagicMock(return_value=db_entity)

        response = self.proxy.get_popular_tables(num_entries=2)

        expected = [
            PopularTable(database=self.db, cluster=self.cluster, schema=self.schema,
                         name=self.entity1['attributes']['qualifiedName']),
            PopularTable(database=self.db, cluster=self.cluster, schema=self.schema,
                         name=self.entity2['attributes']['qualifiedName']),
        ]

        self.assertEqual(response.__repr__(), expected.__repr__())

    @patch.object(AtlasProxy, '_get_ids_from_basic_search')
    def test_get_popular_tables_without_db(self, mock_basic_search):
        attrs_ent1 = self.entity1['attributes']
        attrs_ent1.pop('db')
        entity1 = MagicMock()
        entity1.attributes = attrs_ent1

        attrs_ent2 = self.entity2['attributes']
        attrs_ent2.pop('db')
        entity2 = MagicMock()
        entity2.attributes = attrs_ent2

        bulk_ent_collection = MagicMock()
        bulk_ent_collection.entities = [entity1, entity2]

        self.proxy._driver.entity_bulk = MagicMock(return_value=[bulk_ent_collection])
        response = self.proxy.get_popular_tables(num_entries=2)

        expected = [
            PopularTable(database='', cluster='', schema=self.schema, name=self.entity1['attributes']['qualifiedName']),
            PopularTable(database='', cluster='', schema=self.schema, name=self.entity2['attributes']['qualifiedName']),
        ]

        self.assertEqual(response.__repr__(), expected.__repr__())


if __name__ == '__main__':
    unittest.main()
