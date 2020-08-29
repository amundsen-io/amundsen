# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import copy
import unittest
from typing import Any, Dict, Optional, cast, List

from amundsen_common.models.popular_table import PopularTable
from amundsen_common.models.table import Column, Statistics, Table, Tag, User, Reader,\
    ProgrammaticDescription, ResourceReport
from atlasclient.exceptions import BadRequest
from unittest.mock import MagicMock, patch
from tests.unit.proxy.fixtures.atlas_test_data import Data, DottedDict

from metadata_service import create_app
from metadata_service.entity.tag_detail import TagDetail
from metadata_service.exception import NotFoundException
from metadata_service.util import UserResourceRel
from metadata_service.entity.resource_type import ResourceType


class TestAtlasProxy(unittest.TestCase, Data):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='metadata_service.config.LocalConfig')
        self.app.config['PROGRAMMATIC_DESCRIPTIONS_EXCLUDE_FILTERS'] = ['spark.*']
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
                self.test_column['guid']: self.test_column
            }
        else:
            mocked_entity.referredEntities = {}
        self.proxy._get_table_entity = MagicMock(return_value=mocked_entity)  # type: ignore
        return mocked_entity

    def _mock_get_bookmark_entity(self, entity: Optional[Any] = None) -> Any:
        entity = entity or self.entity1
        mocked_entity = MagicMock()
        mocked_entity.entity = entity
        self.proxy._get_bookmark_entity = MagicMock(return_value=mocked_entity)  # type: ignore
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
        ent = self.proxy._get_table_entity(table_uri=self.table_uri)

        self.assertEqual(ent.__repr__(), unique_attr_response.__repr__())

    def _create_mocked_report_entities_collection(self) -> None:
        mocked_report_entities_collection = MagicMock()
        mocked_report_entities_collection.entities = []
        for entity in self.report_entities:
            mocked_report_entity = MagicMock()
            mocked_report_entity.status = entity['status']
            mocked_report_entity.attributes = entity['attributes']
            mocked_report_entities_collection.entities.append(mocked_report_entity)

        self.report_entity_collection = [mocked_report_entities_collection]

    def _get_table(self, custom_stats_format: bool = False) -> None:
        if custom_stats_format:
            test_exp_col = self.test_exp_col_stats_formatted
        else:
            test_exp_col = self.test_exp_col_stats_raw
        ent_attrs = cast(dict, self.entity1['attributes'])
        self._mock_get_table_entity()
        self._create_mocked_report_entities_collection()
        self.proxy._get_owners = MagicMock(return_value=[User(email=ent_attrs['owner'])])   # type: ignore
        self.proxy._driver.entity_bulk = MagicMock(return_value=self.report_entity_collection)
        response = self.proxy.get_table(table_uri=self.table_uri)

        classif_name = self.classification_entity['classifications'][0]['typeName']

        col_attrs = cast(dict, self.test_column['attributes'])
        exp_col_stats = list()

        for stats in test_exp_col:
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
                         resource_reports=[ResourceReport(name='test_report', url='http://test'),
                                           ResourceReport(name='test_report3', url='http://test3')],
                         last_updated_timestamp=int(str(self.entity1['updateTime'])[:10]),
                         columns=[exp_col] * self.active_columns,
                         programmatic_descriptions=[ProgrammaticDescription(source='test parameter key a',
                                                                            text='testParameterValueA'),
                                                    ProgrammaticDescription(source='test parameter key b',
                                                                            text='testParameterValueB')
                                                    ],
                         is_view=False)

        self.assertEqual(str(expected), str(response))

    def test_get_table_without_custom_stats_format(self) -> None:
        self._get_table()

    def test_get_table_with_custom_stats_format(self) -> None:
        statistics_format_spec = {'min': {'new_name': 'minimum', 'format': '{:,.2f}'},
                                  'max': {'drop': True}}

        with patch.object(self.proxy, 'STATISTICS_FORMAT_SPEC', statistics_format_spec):
            self._get_table(custom_stats_format=True)

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
        ent1 = self.to_class(self.entity1)
        ent2 = self.to_class(self.entity2)

        table_collection = MagicMock()

        table_collection.entities = [ent1, ent2]

        result = MagicMock(return_value=table_collection)

        with patch.object(self.proxy._driver.search_basic, 'create', result):
            response = self.proxy.get_popular_tables(num_entries=2)

            ent1_attrs = cast(dict, self.entity1['attributes'])
            ent2_attrs = cast(dict, self.entity2['attributes'])

            expected = [
                PopularTable(database=self.entity_type, cluster=self.cluster, schema=self.db,
                             name=ent1_attrs['name'], description=ent1_attrs['description']),
                PopularTable(database=self.entity_type, cluster=self.cluster, schema=self.db,
                             name=ent2_attrs['name'], description=ent1_attrs['description']),
            ]

            self.assertEqual(expected.__repr__(), response.__repr__())

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
        user_guid = 123
        self._mock_get_table_entity()
        self.proxy._driver.entity_post = MagicMock()
        self.proxy._driver.entity_post.create = MagicMock(return_value={"guidAssignments": {user_guid: user_guid}})

        with patch.object(self.proxy._driver.relationship, 'create') as mock_execute:
            self.proxy.add_owner(table_uri=self.table_uri, owner=owner)
            mock_execute.assert_called_with(
                data={'typeName': 'DataSet_Users_Owner',
                      'end1': {'guid': self.entity1['guid'], 'typeName': 'Table'},
                      'end2': {'guid': user_guid, 'typeName': 'User'}}
            )

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

    def test_get_table_by_user_relation_follow(self) -> None:
        bookmark1 = copy.deepcopy(self.bookmark_entity1)
        bookmark1 = self.to_class(bookmark1)
        bookmark_collection = MagicMock()
        bookmark_collection.entities = [bookmark1]

        self.proxy._driver.search_basic.create = MagicMock(return_value=bookmark_collection)
        res = self.proxy.get_table_by_user_relation(user_email='test_user_id',
                                                    relation_type=UserResourceRel.follow)

        expected = [PopularTable(database=Data.entity_type, cluster=Data.cluster, schema=Data.db,
                                 name=Data.name, description=None)]

        self.assertEqual(res, {'table': expected})

    def test_get_table_by_user_relation_own(self) -> None:
        unique_attr_response = MagicMock()
        unique_attr_response.entity = Data.user_entity_2
        self.proxy._driver.entity_unique_attribute = MagicMock(return_value=unique_attr_response)

        entity_bulk_result = MagicMock()
        entity_bulk_result.entities = [DottedDict(self.entity1)]
        self.proxy._driver.entity_bulk = MagicMock(return_value=[entity_bulk_result])

        res = self.proxy.get_table_by_user_relation(user_email='test_user_id',
                                                    relation_type=UserResourceRel.own)

        ent1_attrs = cast(dict, self.entity1['attributes'])

        expected = [PopularTable(database=self.entity_type, cluster=self.cluster, schema=self.db,
                                 name=ent1_attrs['name'], description=ent1_attrs['description'])]

        self.assertEqual({'table': expected}, res)

    def test_add_resource_relation_by_user(self) -> None:
        bookmark_entity = self._mock_get_bookmark_entity()
        with patch.object(bookmark_entity, 'update') as mock_execute:
            self.proxy.add_resource_relation_by_user(id=self.table_uri,
                                                     user_id="test_user_id",
                                                     relation_type=UserResourceRel.follow,
                                                     resource_type=ResourceType.Table)
            mock_execute.assert_called_with()

    def test_delete_resource_relation_by_user(self) -> None:
        bookmark_entity = self._mock_get_bookmark_entity()
        with patch.object(bookmark_entity, 'update') as mock_execute:
            self.proxy.delete_resource_relation_by_user(id=self.table_uri,
                                                        user_id="test_user_id",
                                                        relation_type=UserResourceRel.follow,
                                                        resource_type=ResourceType.Table)
            mock_execute.assert_called_with()

    def test_get_readers(self) -> None:
        basic_search_result = MagicMock()
        basic_search_result.entities = self.reader_entities

        self.proxy._driver.search_basic.create = MagicMock(return_value=basic_search_result)

        entity_bulk_result = MagicMock()
        entity_bulk_result.entities = self.reader_entities
        self.proxy._driver.entity_bulk = MagicMock(return_value=[entity_bulk_result])

        res = self.proxy._get_readers('dummy', 1)

        expected: List[Reader] = []

        expected += [Reader(user=User(email='test_user_1', user_id='test_user_1'), read_count=5)]
        expected += [Reader(user=User(email='test_user_2', user_id='test_user_2'), read_count=150)]

        self.assertEqual(res, expected)

    def test_get_frequently_used_tables(self) -> None:
        entity_unique_attribute_result = MagicMock()
        entity_unique_attribute_result.entity = DottedDict(self.user_entity_2)
        self.proxy._driver.entity_unique_attribute = MagicMock(return_value=entity_unique_attribute_result)

        entity_bulk_result = MagicMock()
        entity_bulk_result.entities = [DottedDict(self.reader_entity_1)]
        self.proxy._driver.entity_bulk = MagicMock(return_value=[entity_bulk_result])

        expected = {'table': [PopularTable(cluster=self.cluster,
                                           name='Table1',
                                           schema=self.db,
                                           database=self.entity_type)]}

        res = self.proxy.get_frequently_used_tables(user_email='dummy')

        self.assertEqual(expected, res)

    def test_get_latest_updated_ts_when_exists(self) -> None:
        with patch.object(self.proxy._driver, 'admin_metrics', self.metrics_data):
            result = self.proxy.get_latest_updated_ts()

            assert result == 1598342400

    def test_get_latest_updated_ts_when_not_exists(self) -> None:
        with patch.object(self.proxy._driver, 'admin_metrics', []):
            result = self.proxy.get_latest_updated_ts()

            assert result == 0


if __name__ == '__main__':
    unittest.main()
