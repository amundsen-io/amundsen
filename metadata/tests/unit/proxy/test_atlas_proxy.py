import copy
import unittest
from typing import Any, Dict, Optional, cast

from amundsen_common.models.popular_table import PopularTable
from amundsen_common.models.table import Column, Statistics, Table, Tag, User
from atlasclient.exceptions import BadRequest
from mock import MagicMock, patch
from tests.unit.proxy.fixtures.atlas_test_data import Data

from metadata_service import create_app
from metadata_service.entity.tag_detail import TagDetail
from metadata_service.exception import NotFoundException
from metadata_service.util import UserResourceRel
from metadata_service.entity.resource_type import ResourceType


class TestAtlasProxy(unittest.TestCase, Data):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='metadata_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

        with patch('metadata_service.proxy.atlas_proxy.Atlas'):
            # Importing here to make app context work before
            # importing `current_app` indirectly using the AtlasProxy
            from metadata_service.proxy.atlas_proxy import AtlasProxy
            self.proxy = AtlasProxy(host='DOES_NOT_MATTER', port=0000)
            self.proxy._driver = MagicMock()

    def to_class(self, entity: Dict) -> Any:
        class ObjectView(object):
            def __init__(self, dictionary: Dict):
                self.__dict__ = dictionary

        return ObjectView(entity)

    def _mock_get_table_entity(self, entity: Optional[Any] = None) -> Any:
        entity = cast(dict, entity or self.entity1)
        mocked_entity = MagicMock()
        mocked_entity.entity = entity
        if mocked_entity.entity == self.entity1:
            mocked_entity.referredEntities = {
                self.test_column['guid']: self.test_column,
                self.column_metadata_entity['guid']: self.column_metadata_entity
            }
        else:
            mocked_entity.referredEntities = {}
        self.proxy._get_table_entity = MagicMock(return_value=(mocked_entity, {    # type: ignore
            'entity': self.entity_type,
            'cluster': self.cluster,
            'db': self.db,
            'name': entity['attributes']['name']
        }))
        return mocked_entity

    def _mock_get_reader_entity(self, entity: Optional[Any] = None) -> Any:
        entity = entity or self.entity1
        mocked_entity = MagicMock()
        mocked_entity.entity = entity
        self.proxy._get_reader_entity = MagicMock(return_value=mocked_entity)    # type: ignore
        return mocked_entity

    def test_extract_table_uri_info(self) -> None:
        table_info = self.proxy._extract_info_from_uri(table_uri=self.table_uri)
        self.assertDictEqual(table_info, {
            'entity': self.entity_type,
            'cluster': self.cluster,
            'db': self.db,
            'name': self.name
        })

    def test_get_ids_from_basic_search(self) -> None:
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

    def test_get_table_entity(self) -> None:
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

    def test_get_table(self) -> None:
        self._mock_get_table_entity()
        response = self.proxy.get_table(table_uri=self.table_uri)

        classif_name = self.classification_entity['classifications'][0]['typeName']
        ent_attrs = cast(dict, self.entity1['attributes'])

        col_attrs = cast(dict, self.test_column['attributes'])
        col_metadata_attrs = cast(dict, self.column_metadata_entity['attributes'])
        exp_col_stats = list()

        for stats in col_metadata_attrs['statistics']:
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
                         last_updated_timestamp=cast(int, self.entity1['updateTime']))
        self.assertEqual(str(expected), str(response))

    def test_get_table_not_found(self) -> None:
        with self.assertRaises(NotFoundException):
            self.proxy._driver.entity_unique_attribute = MagicMock(side_effect=Exception('Boom!'))
            self.proxy.get_table(table_uri=self.table_uri)

    def test_get_table_missing_info(self) -> None:
        with self.assertRaises(BadRequest):
            local_entity = copy.deepcopy(self.entity1)
            local_entity.pop('attributes')
            unique_attr_response = MagicMock()
            unique_attr_response.entity = local_entity

            self.proxy._driver.entity_unique_attribute = MagicMock(return_value=unique_attr_response)
            self.proxy.get_table(table_uri=self.table_uri)

    def test_get_popular_tables(self) -> None:
        meta1: Dict = copy.deepcopy(self.metadata1)
        meta2: Dict = copy.deepcopy(self.metadata2)

        meta1['attributes']['table'] = self.entity1
        meta2['attributes']['table'] = self.entity2

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

            ent1_attrs = cast(dict, self.entity1['attributes'])
            ent2_attrs = cast(dict, self.entity2['attributes'])

            expected = [
                PopularTable(database=self.entity_type, cluster=self.cluster, schema=self.db,
                             name=ent1_attrs['name'], description=ent1_attrs['description']),
                PopularTable(database=self.entity_type, cluster=self.cluster, schema=self.db,
                             name=ent2_attrs['name'], description=ent1_attrs['description']),
            ]

            self.assertEqual(expected.__repr__(), response.__repr__())

    # noinspection PyTypeChecker
    def test_get_popular_tables_without_db(self) -> None:
        meta1: Dict = copy.deepcopy(self.metadata1)
        meta2: Dict = copy.deepcopy(self.metadata2)

        meta1['attributes']['table'] = self.entity1
        meta2['attributes']['table'] = self.entity2

        metadata1 = self.to_class(meta1)
        metadata2 = self.to_class(meta2)

        metadata_collection = MagicMock()
        metadata_collection.entities = [metadata1, metadata2]

        result = MagicMock(return_value=metadata_collection)

        with patch.object(self.proxy._driver.search_basic, 'create', result):
            entity1: Dict = copy.deepcopy(self.entity1)
            entity2: Dict = copy.deepcopy(self.entity2)

            for entity in [entity1, entity2]:
                entity['attributes']['qualifiedName'] = entity['attributes']['name']

            entities_collection = MagicMock()
            entities_collection.entities = [self.to_class(entity1), self.to_class(entity2)]

            # Invalidate the cache to test the cache functionality
            popular_query_params = {'typeName': 'table_metadata',
                                    'sortBy': 'popularityScore',
                                    'sortOrder': 'DESCENDING',
                                    'excludeDeletedEntities': True,
                                    'limit': 2,
                                    'attributes': ['table']}
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

            ent1_attrs = cast(dict, self.entity1['attributes'])
            ent2_attrs = cast(dict, self.entity2['attributes'])

            expected = [
                PopularTable(database=self.entity_type, cluster='default', schema='default',
                             name=ent1_attrs['name'], description=ent1_attrs['description']),
                PopularTable(database=self.entity_type, cluster='default', schema='default',
                             name=ent2_attrs['name'], description=ent1_attrs['description']),
            ]

            self.assertEqual(expected.__repr__(), response.__repr__())

    def test_get_popular_tables_search_exception(self) -> None:
        with self.assertRaises(NotFoundException):
            self.proxy._driver.entity_bulk = MagicMock(return_value=None)
            self.proxy._get_metadata_entities({'query': 'test'})

    def test_get_table_description(self) -> None:
        self._mock_get_table_entity()
        response = self.proxy.get_table_description(table_uri=self.table_uri)
        attributes = cast(dict, self.entity1['attributes'])
        self.assertEqual(response, attributes['description'])

    def test_put_table_description(self) -> None:
        self._mock_get_table_entity()
        self.proxy.put_table_description(table_uri=self.table_uri,
                                         description="DOESNT_MATTER")

    def test_get_tags(self) -> None:
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

    def test_add_tag(self) -> None:
        tag = "TAG"
        self._mock_get_table_entity()

        with patch.object(self.proxy._driver.entity_bulk_classification, 'create') as mock_execute:
            self.proxy.add_tag(id=self.table_uri, tag=tag, tag_type='default')
            mock_execute.assert_called_with(
                data={'classification': {'typeName': tag}, 'entityGuids': [self.entity1['guid']]}
            )

    def test_delete_tag(self) -> None:
        tag = "TAG"
        self._mock_get_table_entity()
        mocked_entity = MagicMock()
        self.proxy._driver.entity_guid = MagicMock(return_value=mocked_entity)

        with patch.object(mocked_entity.classifications(tag), 'delete') as mock_execute:
            self.proxy.delete_tag(id=self.table_uri, tag=tag, tag_type='default')
            mock_execute.assert_called_with()

    def test_add_owner(self) -> None:
        owner = "OWNER"
        entity = self._mock_get_table_entity()
        with patch.object(entity, 'update') as mock_execute:
            self.proxy.add_owner(table_uri=self.table_uri, owner=owner)
            mock_execute.assert_called_with()

    def test_get_column(self) -> None:
        self._mock_get_table_entity()
        response = self.proxy._get_column(
            table_uri=self.table_uri,
            column_name=cast(dict, self.test_column['attributes'])['name'])
        self.assertDictEqual(response, self.test_column)

    def test_get_column_wrong_name(self) -> None:
        with self.assertRaises(NotFoundException):
            self._mock_get_table_entity()
            self.proxy._get_column(table_uri=self.table_uri, column_name='FAKE')

    def test_get_column_no_referred_entities(self) -> None:
        with self.assertRaises(NotFoundException):
            local_entity: Dict = self.entity2
            local_entity['attributes']['columns'] = [{'guid': 'ent_2_col'}]
            self._mock_get_table_entity(local_entity)
            self.proxy._get_column(table_uri=self.table_uri, column_name='FAKE')

    def test_get_column_description(self) -> None:
        self._mock_get_table_entity()
        attributes = cast(dict, self.test_column['attributes'])
        response = self.proxy.get_column_description(
            table_uri=self.table_uri,
            column_name=attributes['name'])
        self.assertEqual(response, attributes.get('description'))

    def test_put_column_description(self) -> None:
        self._mock_get_table_entity()
        attributes = cast(dict, self.test_column['attributes'])
        self.proxy.put_column_description(table_uri=self.table_uri,
                                          column_name=attributes['name'],
                                          description='DOESNT_MATTER')

    def test_get_table_by_user_relation(self) -> None:
        reader1 = copy.deepcopy(self.reader_entity1)
        reader1 = self.to_class(reader1)
        reader_collection = MagicMock()
        reader_collection.entities = [reader1]

        self.proxy._driver.search_basic.create = MagicMock(return_value=reader_collection)
        res = self.proxy.get_table_by_user_relation(user_email='test_user_id',
                                                    relation_type=UserResourceRel.follow)

        expected = [PopularTable(database=Data.entity_type, cluster=Data.cluster, schema=Data.db,
                                 name=Data.name, description=None)]

        self.assertEqual(res, {'table': expected})

    def test_add_resource_relation_by_user(self) -> None:
        reader_entity = self._mock_get_reader_entity()
        with patch.object(reader_entity, 'update') as mock_execute:
            self.proxy.add_resource_relation_by_user(id=self.table_uri,
                                                     user_id="test_user_id",
                                                     relation_type=UserResourceRel.follow,
                                                     resource_type=ResourceType.Table)
            mock_execute.assert_called_with()

    def test_delete_resource_relation_by_user(self) -> None:
        reader_entity = self._mock_get_reader_entity()
        with patch.object(reader_entity, 'update') as mock_execute:
            self.proxy.delete_resource_relation_by_user(id=self.table_uri,
                                                        user_id="test_user_id",
                                                        relation_type=UserResourceRel.follow,
                                                        resource_type=ResourceType.Table)
            mock_execute.assert_called_with()


if __name__ == '__main__':
    unittest.main()
