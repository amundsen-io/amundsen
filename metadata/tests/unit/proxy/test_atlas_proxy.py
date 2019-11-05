import copy
import unittest

from atlasclient.exceptions import BadRequest
from mock import patch, MagicMock

from metadata_service import create_app
from metadata_service.entity.popular_table import PopularTable
from metadata_service.entity.table_detail import (Table, User, Tag, Column, Statistics)
from metadata_service.entity.tag_detail import TagDetail
from metadata_service.exception import NotFoundException
from tests.unit.proxy.fixtures.atlas_test_data import Data


class TestAtlasProxy(unittest.TestCase, Data):
    def setUp(self):
        self.app = create_app(config_module_class='metadata_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

        with patch('metadata_service.proxy.atlas_proxy.Atlas'):
            # Importing here to make app context work before
            # importing `current_app` indirectly using the AtlasProxy
            from metadata_service.proxy.atlas_proxy import AtlasProxy
            self.proxy = AtlasProxy(host='DOES_NOT_MATTER', port=0000)
            self.proxy._driver = MagicMock()

    def to_class(self, entity):
        class ObjectView(object):
            def __init__(self, dictionary):
                self.__dict__ = dictionary

        return ObjectView(entity)

    def _mock_get_table_entity(self, entity=None):
        entity = entity or self.entity1
        mocked_entity = MagicMock()
        mocked_entity.entity = entity
        if mocked_entity.entity == self.entity1:
            mocked_entity.referredEntities = {
                self.test_column['guid']: self.test_column
            }
        else:
            mocked_entity.referredEntities = {}
        self.proxy._get_table_entity = MagicMock(return_value=(mocked_entity, {
            'entity': self.entity_type,
            'cluster': self.cluster,
            'db': self.db,
            'name': entity['attributes']['name']
        }))
        return mocked_entity

    def _mock_get_reader_entity(self, entity=None):
        entity = entity or self.entity1
        mocked_entity = MagicMock()
        mocked_entity.entity = entity
        self.proxy._get_reader_entity = MagicMock(return_value=mocked_entity)
        return mocked_entity

    def test_extract_table_uri_info(self):
        table_info = self.proxy._extract_info_from_uri(table_uri=self.table_uri)
        self.assertDictEqual(table_info, {
            'entity': self.entity_type,
            'cluster': self.cluster,
            'db': self.db,
            'name': self.name
        })

    def test_get_ids_from_basic_search(self):
        entity1 = MagicMock()
        entity1.guid = self.entity1['guid']

        entity2 = MagicMock()
        entity2.guid = self.entity2['guid']

        basic_search_response = MagicMock()
        basic_search_response.entities = [entity1, entity2]

        self.proxy._driver.search_basic = MagicMock(return_value=[basic_search_response])
        response = self.proxy._get_ids_from_basic_search(params={})
        expected = ['1', '2']
        self.assertListEqual(response, expected)

    def test_get_table_entity(self):
        unique_attr_response = MagicMock()

        self.proxy._driver.entity_unique_attribute = MagicMock(
            return_value=unique_attr_response)
        ent, table_info = self.proxy._get_table_entity(table_uri=self.table_uri)
        self.assertDictEqual(table_info, {
            'entity': self.entity_type,
            'cluster': self.cluster,
            'db': self.db,
            'name': self.name
        })
        self.assertEqual(ent.__repr__(), unique_attr_response.__repr__())

    def test_get_table(self):
        self._mock_get_table_entity()
        response = self.proxy.get_table(table_uri=self.table_uri)

        classif_name = self.classification_entity['classifications'][0]['typeName']
        ent_attrs = self.entity1['attributes']

        col_attrs = self.test_column['attributes']
        exp_col_stats = list()

        for stats in col_attrs['stats']:
            exp_col_stats.append(
                Statistics(
                    stat_type=stats['attributes']['stat_name'],
                    stat_val=stats['attributes']['stat_val'],
                    start_epoch=stats['attributes']['start_epoch'],
                    end_epoch=stats['attributes']['end_epoch'],
                )
            )
        exp_col = Column(name=col_attrs['name'],
                         description='column description',
                         col_type='Managed',
                         sort_order=col_attrs['position'],
                         stats=exp_col_stats)
        expected = Table(database=self.entity_type,
                         cluster=self.cluster,
                         schema=self.db,
                         name=ent_attrs['name'],
                         tags=[Tag(tag_name=classif_name, tag_type="default")],
                         description=ent_attrs['description'],
                         owners=[User(email=ent_attrs['owner'])],
                         columns=[exp_col],
                         last_updated_timestamp=self.entity1['updateTime'])
        self.assertEqual(str(expected), str(response))

    def test_get_table_not_found(self):
        with self.assertRaises(NotFoundException):
            self.proxy._driver.entity_unique_attribute = MagicMock(side_effect=Exception('Boom!'))
            self.proxy.get_table(table_uri=self.table_uri)

    def test_get_table_missing_info(self):
        with self.assertRaises(BadRequest):
            local_entity = copy.deepcopy(self.entity1)
            local_entity.pop('attributes')
            unique_attr_response = MagicMock()
            unique_attr_response.entity = local_entity

            self.proxy._driver.entity_unique_attribute = MagicMock(return_value=unique_attr_response)
            self.proxy.get_table(table_uri=self.table_uri)

    def test_get_popular_tables(self):
        meta1 = copy.deepcopy(self.metadata1)
        meta2 = copy.deepcopy(self.metadata2)

        meta1['attributes']['parentEntity'] = self.entity1
        meta2['attributes']['parentEntity'] = self.entity2

        metadata1 = self.to_class(meta1)
        metadata2 = self.to_class(meta2)

        metadata_collection = MagicMock()
        metadata_collection.entities = [metadata1, metadata2]

        result = MagicMock(return_value=metadata_collection)

        with patch.object(self.proxy._driver.search_basic, 'create', result):
            entities_collection = MagicMock()
            entities_collection.entities = [self.to_class(self.entity1), self.to_class(self.entity2)]

            self.proxy._driver.entity_bulk = MagicMock(return_value=[entities_collection])

            response = self.proxy.get_popular_tables(num_entries=2)

            # Call multiple times for cache test.
            self.proxy.get_popular_tables(num_entries=2)
            self.proxy.get_popular_tables(num_entries=2)
            self.proxy.get_popular_tables(num_entries=2)
            self.proxy.get_popular_tables(num_entries=2)

            self.assertEqual(self.proxy._driver.entity_bulk.call_count, 1)

            ent1_attrs = self.entity1['attributes']
            ent2_attrs = self.entity2['attributes']

            expected = [
                PopularTable(database=self.entity_type, cluster=self.cluster, schema=self.db,
                             name=ent1_attrs['name'], description=ent1_attrs['description']),
                PopularTable(database=self.entity_type, cluster=self.cluster, schema=self.db,
                             name=ent2_attrs['name'], description=ent1_attrs['description']),
            ]

            self.assertEqual(expected.__repr__(), response.__repr__())

    # noinspection PyTypeChecker
    def test_get_popular_tables_without_db(self):
        meta1 = copy.deepcopy(self.metadata1)
        meta2 = copy.deepcopy(self.metadata2)

        meta1['attributes']['parentEntity'] = self.entity1
        meta2['attributes']['parentEntity'] = self.entity2

        metadata1 = self.to_class(meta1)
        metadata2 = self.to_class(meta2)

        metadata_collection = MagicMock()
        metadata_collection.entities = [metadata1, metadata2]

        result = MagicMock(return_value=metadata_collection)

        with patch.object(self.proxy._driver.search_basic, 'create', result):
            entity1 = copy.deepcopy(self.entity1)
            entity2 = copy.deepcopy(self.entity2)

            for entity in [entity1, entity2]:
                entity['attributes']['qualifiedName'] = entity['attributes']['name']

            entities_collection = MagicMock()
            entities_collection.entities = [self.to_class(entity1), self.to_class(entity2)]

            # Invalidate the cache to test the cache functionality
            popular_query_params = {'typeName': 'Metadata',
                                    'sortBy': 'popularityScore',
                                    'sortOrder': 'DESCENDING',
                                    'excludeDeletedEntities': True,
                                    'limit': 2,
                                    'attributes': ['parentEntity']}
            self.proxy._CACHE.region_invalidate(self.proxy._get_metadata_entities,
                                                None, '_get_metadata_entities',
                                                popular_query_params)

            self.proxy._driver.entity_bulk = MagicMock(return_value=[entities_collection])
            response = self.proxy.get_popular_tables(num_entries=2)

            # Call multiple times for cache test.
            self.proxy.get_popular_tables(num_entries=2)
            self.proxy.get_popular_tables(num_entries=2)
            self.proxy.get_popular_tables(num_entries=2)
            self.proxy.get_popular_tables(num_entries=2)

            self.assertEqual(1, self.proxy._driver.entity_bulk.call_count)

            ent1_attrs = self.entity1['attributes']
            ent2_attrs = self.entity2['attributes']

            expected = [
                PopularTable(database=self.entity_type, cluster='default', schema='default',
                             name=ent1_attrs['name'], description=ent1_attrs['description']),
                PopularTable(database=self.entity_type, cluster='default', schema='default',
                             name=ent2_attrs['name'], description=ent1_attrs['description']),
            ]

            self.assertEqual(expected.__repr__(), response.__repr__())

    def test_get_popular_tables_search_exception(self):
        with self.assertRaises(NotFoundException):
            self.proxy._driver.entity_bulk = MagicMock(return_value=None)
            self.proxy._get_metadata_entities({'query': 'test'})

    def test_get_table_description(self):
        self._mock_get_table_entity()
        response = self.proxy.get_table_description(table_uri=self.table_uri)
        self.assertEqual(response, self.entity1['attributes']['description'])

    def test_put_table_description(self):
        self._mock_get_table_entity()
        self.proxy.put_table_description(table_uri=self.table_uri,
                                         description="DOESNT_MATTER")

    def test_get_tags(self):
        tag_response = {
            'tagEntities': {
                'PII': 3,
                'NON_PII': 2
            }
        }

        mocked_metrics = MagicMock()
        mocked_metrics.tag = tag_response

        self.proxy._driver.admin_metrics = [mocked_metrics]

        response = self.proxy.get_tags()

        expected = [TagDetail(tag_name='PII', tag_count=3), TagDetail(tag_name='NON_PII', tag_count=2)]
        self.assertEqual(expected.__repr__(), response.__repr__())

    def test_add_tag(self):
        tag = "TAG"
        self._mock_get_table_entity()

        with patch.object(self.proxy._driver.entity_bulk_classification, 'create') as mock_execute:
            self.proxy.add_tag(table_uri=self.table_uri, tag=tag)
            mock_execute.assert_called_with(
                data={'classification': {'typeName': tag}, 'entityGuids': [self.entity1['guid']]}
            )

    def test_delete_tag(self):
        tag = "TAG"
        self._mock_get_table_entity()
        mocked_entity = MagicMock()
        self.proxy._driver.entity_guid = MagicMock(return_value=mocked_entity)

        with patch.object(mocked_entity.classifications(tag), 'delete') as mock_execute:
            self.proxy.delete_tag(table_uri=self.table_uri, tag=tag)
            mock_execute.assert_called_with()

    def test_add_owner(self):
        owner = "OWNER"
        entity = self._mock_get_table_entity()
        with patch.object(entity, 'update') as mock_execute:
            self.proxy.add_owner(table_uri=self.table_uri, owner=owner)
            mock_execute.assert_called_with()

    def test_get_column(self):
        self._mock_get_table_entity()
        response = self.proxy._get_column(
            table_uri=self.table_uri,
            column_name=self.test_column['attributes']['name'])
        self.assertDictEqual(response, self.test_column)

    def test_get_column_wrong_name(self):
        with self.assertRaises(NotFoundException):
            self._mock_get_table_entity()
            self.proxy._get_column(table_uri=self.table_uri, column_name='FAKE')

    def test_get_column_no_referred_entities(self):
        with self.assertRaises(NotFoundException):
            local_entity = self.entity2
            local_entity['attributes']['columns'] = [{'guid': 'ent_2_col'}]
            self._mock_get_table_entity(local_entity)
            self.proxy._get_column(table_uri=self.table_uri, column_name='FAKE')

    def test_get_column_description(self):
        self._mock_get_table_entity()
        response = self.proxy.get_column_description(
            table_uri=self.table_uri,
            column_name=self.test_column['attributes']['name'])
        self.assertEqual(response, self.test_column['attributes'].get('description'))

    def test_put_column_description(self):
        self._mock_get_table_entity()
        self.proxy.put_column_description(table_uri=self.table_uri,
                                          column_name=self.test_column['attributes']['name'],
                                          description='DOESNT_MATTER')

    def test_get_table_by_user_relation(self):

        reader1 = copy.deepcopy(self.reader_entity1)
        reader1 = self.to_class(reader1)
        reader_collection = MagicMock()
        reader_collection.entities = [reader1]

        self.proxy._driver.search_basic.create = MagicMock(return_value=reader_collection)
        res = self.proxy.get_table_by_user_relation(user_email='test_user_id',
                                                    relation_type='follow')

        expected = [PopularTable(database=Data.entity_type, cluster=Data.cluster, schema=Data.db,
                                 name=Data.name, description=None)]

        self.assertEqual(res, {'table': expected})

    def test_add_resource_relation_by_user(self):
        reader_entity = self._mock_get_reader_entity()
        with patch.object(reader_entity, 'update') as mock_execute:
            self.proxy.add_table_relation_by_user(table_uri=self.table_uri,
                                                  user_email="test_user_id",
                                                  relation_type='follow')
            mock_execute.assert_called_with()

    def test_delete_resource_relation_by_user(self):
        reader_entity = self._mock_get_reader_entity()
        with patch.object(reader_entity, 'update') as mock_execute:
            self.proxy.delete_table_relation_by_user(table_uri=self.table_uri,
                                                     user_email="test_user_id",
                                                     relation_type='follow')
            mock_execute.assert_called_with()


if __name__ == '__main__':
    unittest.main()
