# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import copy
import textwrap
import unittest
from collections import namedtuple
from typing import Any, Dict  # noqa: F401
from unittest.mock import MagicMock, patch

from jinja2 import Template

from amundsen_common.entity.resource_type import ResourceType
from amundsen_common.models.api import health_check
from amundsen_common.models.dashboard import DashboardSummary
from amundsen_common.models.feature import Feature
from amundsen_common.models.generation_code import GenerationCode
from amundsen_common.models.lineage import Lineage, LineageItem
from amundsen_common.models.popular_table import PopularTable
from amundsen_common.models.table import (Application, Badge, Column,
                                          ProgrammaticDescription, Reader,
                                          ResourceReport, Source, SqlJoin,
                                          SqlWhere, Table, TableSummary,
                                          Tag, TypeMetadata, User, Watermark)
from amundsen_common.models.user import User as UserModel

from metadata_service import create_app
from metadata_service.entity.dashboard_detail import DashboardDetail
from metadata_service.entity.tag_detail import TagDetail
from metadata_service.exception import NotFoundException
from metadata_service.proxy.nebula_proxy import NebulaProxy
from metadata_service.util import UserResourceRel


class TestNebulaProxy(unittest.TestCase):

    def setUp(self) -> None:
        self.app = create_app(
            config_module_class='metadata_service.config.NebulaConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.col_usage_return_value = [{
            'spaceName':
            'amundsen',
            'data': [{
                'meta':
                [{
                    'type': 'vertex',
                    'id': 'database://delta'
                }, {
                    'type': 'vertex',
                    'id': 'delta://gold'
                }, {
                    'type': 'vertex',
                    'id': 'delta://gold.test_schema'
                }, {
                    'type': 'vertex',
                    'id': 'delta://gold.test_schema/delta_test_table'
                }, {
                    'type': 'vertex',
                    'id':
                    'delta://gold.test_schema/delta_test_table/_description'
                }, {
                    'type': 'vertex',
                    'id': 'delta://gold.test_schema/delta_test_table/col1'
                },
                 {
                     'type':
                     'vertex',
                     'id':
                     'delta://gold.test_schema/delta_test_table/col1/_description'
                 }, [], [],
                 [[[{
                     'type':
                     'vertex',
                     'id': 'pk'
                 }, {
                     'type':
                     'vertex',
                     'id': 'pii'
                 }], {
                     'type':
                     'vertex',
                     'id':
                     'delta://gold.test_schema/delta_test_table/col1/type/col2/_description'
                 }, {
                     'type':
                     'vertex',
                     'id':
                     'delta://gold.test_schema/delta_test_table/col1/type/col1'
                 }]], None],
                'row': [
                    {
                        'Database.name': 'delta',
                        'Database.published_tag': 'unique_tag',
                        'Database.publisher_last_updated_epoch_ms': 1649259854
                    }, {
                        'Cluster.name': 'gold',
                        'Cluster.publisher_last_updated_epoch_ms': 1649259854,
                        'Cluster.published_tag': 'unique_tag'
                    }, {
                        'Schema.name': 'test_schema',
                        'Schema.publisher_last_updated_epoch_ms': 1649259854,
                        'Schema.published_tag': 'unique_tag'
                    }, {
                        'Table.publisher_last_updated_epoch_ms': 1649259854,
                        'Table.published_tag': 'unique_tag',
                        'Table.name': 'delta_test_table',
                    }, {
                        'Description.published_tag': 'unique_tag',
                        'Description.publisher_last_updated_epoch_ms':
                        1649259854,
                        'Description.description_source': 'description',
                        'Description.description': 'test table for delta'
                    }, {
                        'Column.name': 'col1',
                        'Column.publisher_last_updated_epoch_ms': 1649259854,
                        'Column.col_type': 'bigint',
                        'Column.sort_order': 1,
                        'Column.published_tag': 'unique_tag'
                    }, {
                        'Description.published_tag': 'unique_tag',
                        'Description.publisher_last_updated_epoch_ms':
                        1649259854,
                        'Description.description_source': 'description',
                        'Description.description': 'col1 description'
                    }, [], [],
                    [{
                        'node':
                        {
                            'Type_Metadata.publisher_last_updated_epoch_ms':
                            1649259854,
                            'Type_Metadata.name': 'col1',
                            'Type_Metadata.sort_order': 0,
                            'Type_Metadata.kind': 'scalar',
                            'Type_Metadata.published_tag': 'unique_tag',
                            'Type_Metadata.data_type': 'bigint'
                        },
                        'description': {
                            'Description.published_tag':
                            None,
                            'Description.publisher_last_updated_epoch_ms':
                            None,
                            'Description.description_source':
                            None,
                            'Description.description':
                            'data_type: "bigint", kind: "scalar", name: "col1"'
                        },
                        'badge': [{
                            'Badge.category':
                            'column',
                            'Badge.published_tag':
                            'unique_tag',
                            'Badge.publisher_last_updated_epoch_ms':
                            1649259854
                        }, {
                            'Badge.category':
                            'column',
                            'Badge.published_tag':
                            'unique_tag',
                            'Badge.publisher_last_updated_epoch_ms':
                            1649259854,
                            'Tag.tag_type':
                            'default',
                            'Tag.published_tag':
                            'unique_tag',
                            'Tag.publisher_last_updated_epoch_ms':
                            1649237216
                        }]
                    }], 1
                ]
            }, {
                'meta': [
                    {
                        'type': 'vertex',
                        'id': 'database://delta'
                    }, {
                        'type': 'vertex',
                        'id': 'delta://gold'
                    }, {
                        'type': 'vertex',
                        'id': 'delta://gold.test_schema'
                    }, {
                        'type': 'vertex',
                        'id': 'delta://gold.test_schema/delta_test_table'
                    }, {
                        'type':
                        'vertex',
                        'id':
                        'delta://gold.test_schema/delta_test_table/_description'
                    }, {
                        'type': 'vertex',
                        'id': 'delta://gold.test_schema/delta_test_table/col2'
                    }, {
                        'type':
                        'vertex',
                        'id':
                        'delta://gold.test_schema/delta_test_table/col2/_description'
                    }, [], [],
                    [[[], None, {
                        'type':
                        'vertex',
                        'id':
                        'delta://gold.test_schema/delta_test_table/col2/type/col2/col3'
                    }],
                     [[], None, {
                         'type':
                         'vertex',
                         'id':
                         'delta://gold.test_schema/delta_test_table/col2/type/col2'
                     }],
                     [[], None, {
                         'type':
                         'vertex',
                         'id':
                         'delta://gold.test_schema/delta_test_table/col2/type/col2/col4'
                     }]], None
                ],
                'row': [
                    {
                        'Database.name': 'delta',
                        'Database.published_tag': 'unique_tag',
                        'Database.publisher_last_updated_epoch_ms': 1649259854
                    }, {
                        'Cluster.name': 'gold',
                        'Cluster.publisher_last_updated_epoch_ms': 1649259854,
                        'Cluster.published_tag': 'unique_tag'
                    }, {
                        'Schema.name': 'test_schema',
                        'Schema.publisher_last_updated_epoch_ms': 1649259854,
                        'Schema.published_tag': 'unique_tag'
                    }, {
                        'Table.publisher_last_updated_epoch_ms': 1649259854,
                        'Table.published_tag': 'unique_tag',
                        'Table.name': 'delta_test_table',
                    }, {
                        'Description.published_tag': 'unique_tag',
                        'Description.publisher_last_updated_epoch_ms':
                        1649259854,
                        'Description.description_source': 'description',
                        'Description.description': 'test table for delta'
                    }, {
                        'Column.name': 'col2',
                        'Column.publisher_last_updated_epoch_ms': 1649259854,
                        'Column.col_type': 'struct<col3:string,col4:bigint>',
                        'Column.sort_order': 2,
                        'Column.published_tag': 'unique_tag'
                    }, {
                        'Description.published_tag': 'unique_tag',
                        'Description.publisher_last_updated_epoch_ms':
                        1649259854,
                        'Description.description_source': 'description',
                        'Description.description': 'col2 nested delta column'
                    }, [], [],
                    [{
                        'node':
                        {
                            'Type_Metadata.publisher_last_updated_epoch_ms':
                            1649259854,
                            'Type_Metadata.name': 'col3',
                            'Type_Metadata.sort_order': 0,
                            'Type_Metadata.kind': 'scalar',
                            'Type_Metadata.published_tag': 'unique_tag',
                            'Type_Metadata.data_type': 'string'
                        },
                        'description': None,
                        'badge': []
                    }, {
                        'node': {
                            'Type_Metadata.publisher_last_updated_epoch_ms':
                            1649259854,
                            'Type_Metadata.name':
                            'col2',
                            'Type_Metadata.sort_order':
                            0,
                            'Type_Metadata.kind':
                            'struct',
                            'Type_Metadata.published_tag':
                            'unique_tag',
                            'Type_Metadata.data_type':
                            'struct<col3:string,col4:bigint>'
                        },
                        'description': None,
                        'badge': []
                    }, {
                        'node': {
                            'Type_Metadata.publisher_last_updated_epoch_ms':
                            1649259854,
                            'Type_Metadata.name': 'col4',
                            'Type_Metadata.sort_order': 0,
                            'Type_Metadata.kind': 'scalar',
                            'Type_Metadata.published_tag': 'unique_tag',
                            'Type_Metadata.data_type': 'bigint'
                        },
                        'description': None,
                        'badge': []
                    }], 2
                ]
            }],
            'columns': [
                'db', 'clstr', 'schema', 'tbl', 'tbl_dscrpt', 'col',
                'col_dscrpt', 'col_stats', 'col_badges', 'col_type_metadata',
                'sort_order'
            ],
            'errors': {
                'code': 0
            },
            'latencyInUs': 1
        }]
        self.table_usage_return_value = [{
            'spaceName':
            'amundsen',
            'data': [{
                'meta': [None, None, None],
                'row': ['roald.amundsen@example.org', 500, 'test_table1']
            }, {
                'meta': [None, None, None],
                'row': ['doald3@example.org', 100, 'test_table1']
            }, {
                'meta': [None, None, None],
                'row': ['hoald7@example.org', 100, 'test_table1']
            }, {
                'meta': [None, None, None],
                'row': ['foald5@example.org', 100, 'test_table1']
            }, {
                'meta': [None, None, None],
                'row': ['aoald0@example.org', 100, 'test_table1']
            }],
            'columns': ['email', 'read_count', 'table_name'],
            'errors': {
                'code': 0
            },
            'latencyInUs': 1
        }]

        self.readers_return_value = [{
            'spaceName':
            'amundsen',
            'data': [],
            'columns': ['email', 'read_count', 'table_name'],
            'errors': {
                'code': 0
            },
            'latencyInUs': 1
        }]
        self.table_level_return_value = [{
            'spaceName':
            'amundsen',
            'data': [{
                'meta':
                [[{
                    'type': 'vertex',
                    'id': 'hive://gold.test_schema/test_table1/low_watermark/'
                }, {
                    'type': 'vertex',
                    'id': 'hive://gold.test_schema/test_table1/high_watermark/'
                }],
                 [{
                     'type':
                     'vertex',
                     'id':
                     'application://gold.airflow/event_test/hive.test_schema.test_table1'
                 }], [], None,
                 [{
                     'type': 'vertex',
                     'id': 'roald.amundsen@example.org'
                 }, {
                     'type': 'vertex',
                     'id': 'chrisc@example.org'
                 }],
                 [{
                     'type': 'vertex',
                     'id': 'expensive'
                 }, {
                     'type': 'vertex',
                     'id': 'tag2'
                 }, {
                     'type': 'vertex',
                     'id': 'tag1'
                 }, {
                     'type': 'vertex',
                     'id': 'low_quality'
                 }], [{
                     'type': 'vertex',
                     'id': 'beta'
                 }], {
                     'type': 'vertex',
                     'id': 'hive://gold.test_schema/test_table1/_source'
                 },
                 [{
                     'type':
                     'vertex',
                     'id':
                     'hive://gold.test_schema/test_table1/_s3_crawler_description'
                 }, {
                     'type':
                     'vertex',
                     'id':
                     'hive://gold.test_schema/test_table1/_quality_service_description'
                 }],
                 [{
                     'type':
                     'vertex',
                     'id':
                     'hive://gold.test_schema/test_table1/_report/Advanced Profile'
                 }]],
                'row': [
                    [
                        {
                            'Watermark.create_time': '2019-10-01T12:13:14',
                            'Watermark.partition_key': 'col3',
                            'Watermark.publisher_last_updated_epoch_ms':
                            1649237215,
                            'Watermark.partition_value': '2017-04-22/col4=0',
                            'Watermark.published_tag': 'unique_tag'
                        }, {
                            'Watermark.create_time': '2019-10-01T12:13:14',
                            'Watermark.partition_key': 'col3',
                            'Watermark.publisher_last_updated_epoch_ms':
                            1649237215,
                            'Watermark.partition_value': '2019-09-30/col4=11',
                            'Watermark.published_tag': 'unique_tag'
                        }
                    ],
                    [{
                        'Application.published_tag':
                        'unique_tag',
                        'Application.name':
                        'Airflow',
                        'Application.id':
                        'event_test/hive.test_schema.test_table1',
                        'Application.application_url':
                        'https://airflow_host.net/admin/airflow/tree?dag_id=event_test',
                        'Application.publisher_last_updated_epoch_ms':
                        1649237282,
                        'Application.description':
                        'Airflow with id event_test/hive.test_schema.test_table1'
                    }], [], 1570230473,
                    [{
                        'User.is_active': True,
                        'User.profile_url': '',
                        'User.employee_type': 'sailor',
                        'User.updated_at': 0,
                        'User.last_name': 'Amundsen',
                        'User.slack_id': 'ramundzn',
                        'User.role_name': 'swe',
                        'User.team_name': 'Team Amundsen',
                        'User.full_name': 'Roald Amundsen',
                        'User.first_name': 'Roald',
                        'User.publisher_last_updated_epoch_ms': 1649237216,
                        'User.github_username': 'amundsen-io',
                        'User.manager_fullname': '',
                        'User.user_id': '',
                        'User.email': 'roald.amundsen@example.org',
                        'User.published_tag': 'unique_tag'
                    }, {
                        'User.is_active': True,
                        'User.profile_url': '',
                        'User.employee_type': 'sailor',
                        'User.updated_at': 0,
                        'User.last_name': 'Columbus',
                        'User.slack_id': 'chrisc',
                        'User.role_name': 'swe',
                        'User.team_name': 'Team Amundsen',
                        'User.full_name': 'Christopher Columbus',
                        'User.first_name': 'Christopher',
                        'User.publisher_last_updated_epoch_ms': 1649237216,
                        'User.github_username': 'ChristopherColumbusFAKE',
                        'User.manager_fullname': '',
                        'User.user_id': '',
                        'User.email': 'chrisc@example.org',
                        'User.published_tag': 'unique_tag'
                    }],
                    [{
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649237215
                    }, {
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649259854
                    }, {
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649259854
                    }, {
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649237215
                    }],
                    [{
                        'Badge.category': 'table_status',
                        'Badge.published_tag': 'unique_tag',
                        'Badge.publisher_last_updated_epoch_ms': 1649237214
                    }], {
                        'Source.source_type': 'github',
                        'Source.source':
                        'https://github.com/amundsen-io/amundsen/',
                        'Source.publisher_last_updated_epoch_ms': 1649237216,
                        'Source.published_tag': 'unique_tag'
                    },
                    [{
                        'Programmatic_Description.description':
                        '**Size**: 50T\n\n**Monthly Cost**: $5000',
                        'Programmatic_Description.description_source':
                        's3_crawler',
                        'Programmatic_Description.publisher_last_updated_epoch_ms':
                        1649237215,
                        'Programmatic_Description.published_tag':
                        'unique_tag'
                    }, {
                        'Programmatic_Description.description':
                        '### Quality Report:\n--- \nIpsus enom. Ipsus enom ipsus lorenum.\n---\n[![Build Status](https://api.travis-ci.com/amundsen-io/amundsendatabuilder.svg?branch=master)](https://travis-ci.com/amundsen-io/amundsendatabuilder)',
                        'Programmatic_Description.description_source':
                        'quality_service',
                        'Programmatic_Description.publisher_last_updated_epoch_ms':
                        1649237215,
                        'Programmatic_Description.published_tag':
                        'unique_tag'
                    }],
                    [{
                        'Report.url':
                        'https://pandas-profiling.github.io/pandas-profiling/examples/master/census/census_report.html',
                        'Report.name': 'Advanced Profile',
                        'Report.publisher_last_updated_epoch_ms': 1649237216,
                        'Report.published_tag': 'unique_tag'
                    }]
                ]
            }],
            'columns': [
                'wmk_records', 'producing_apps', 'consuming_apps',
                'last_updated_timestamp', 'owner_records', 'tag_records',
                'badge_records', 'src', 'prog_descriptions', 'resource_reports'
            ],
            'errors': {
                'code': 0
            },
            'latencyInUs': 1
        }]

        self.last_updated_timestamp = 1570230473

        self.table_common_usage = [{
            'spaceName':
            'amundsen',
            'data': [{
                'meta':
                [{
                    'type': 'vertex',
                    'id': 'hive://gold.test_schema/test_table1'
                },
                 [[None, [None, None, None, None, [None, None, None, None]]],
                  [None, [None, None, None, None, [None, None, None, None]]]],
                 [[None, None]]],
                'row': [
                    {
                        'Table.name': 'test_table1',
                        'Table.publisher_last_updated_epoch_ms': 1649259854,
                        'Table.published_tag': 'unique_tag'
                    },
                    [{
                        'join': {
                            'joined_on_table': {
                                'database': 'hive',
                                'cluster': 'gold',
                                'schema': 'test_schema',
                                'name': 'test_table3'
                            },
                            'join_sql':
                            'SELECT * FROM test_table1 inner join test_table3 on test_table1.col2 = test_table3.col1 where test_table1.col5 > 10.0',
                            'joined_on_column': 'col2',
                            'column': 'col2',
                            'join_type': 'inner join'
                        },
                        'join_exec_cnt': 10
                    }, {
                        'join': {
                            'joined_on_table': {
                                'database': 'hive',
                                'cluster': 'gold',
                                'schema': 'test_schema',
                                'name': 'test_table3'
                            },
                            'join_sql':
                            'SELECT * FROM test_table1 inner join test_table3 on test_table1.col2 = test_table3.col1 where test_table1.col5 > 10.0',
                            'joined_on_column': 'col1',
                            'column': 'col2',
                            'join_type': 'inner join'
                        },
                        'join_exec_cnt': 10
                    }],
                    [{
                        'where_clause': 'where test_table1.col5 > 10.0',
                        'where_exec_cnt': 50
                    }]
                ]
            }],
            'columns': ['tbl', 'joins', 'filters'],
            'errors': {
                'code': 0
            },
            'latencyInUs': 1
        }]

        self.col_bar_id_1_expected_type_metadata = self._get_col_bar_id_1_expected_type_metadata(
        )
        self.col_bar_id_2_expected_type_metadata = self._get_col_bar_id_2_expected_type_metadata(
        )

    def _get_col_bar_id_1_expected_type_metadata(self) -> TypeMetadata:
        bar_id_1_c3_map_key_tm = TypeMetadata(
            kind='scalar',
            name='map_key',
            key='hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1'
            '/_inner_/c3/map_key',
            data_type='string',
            sort_order=0)
        bar_id_1_c3_map_value_tm = TypeMetadata(
            kind='scalar',
            name='map_value',
            key='hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1'
            '/_inner_/c3/map_value',
            data_type='string',
            sort_order=0)
        bar_id_1_c4_c5_tm = TypeMetadata(
            kind='scalar',
            name='c5',
            key='hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1'
            '/_inner_/c4/c5',
            data_type='int',
            sort_order=0)
        bar_id_1_c4_c6_tm = TypeMetadata(
            kind='scalar',
            name='c6',
            key='hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1'
            '/_inner_/c4/c6',
            data_type='int',
            sort_order=1)
        bar_id_1_c1_tm = TypeMetadata(
            kind='scalar',
            name='c1',
            key=
            'hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1/_inner_/c1',
            data_type='string',
            sort_order=0)
        bar_id_1_c2_tm = TypeMetadata(
            kind='array',
            name='c2',
            key=
            'hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1/_inner_/c2',
            data_type='array<string>',
            sort_order=1)
        bar_id_1_c3_tm = TypeMetadata(
            kind='map',
            name='c3',
            key=
            'hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1/_inner_/c3',
            data_type='map<string,string>',
            sort_order=2,
            children=[bar_id_1_c3_map_key_tm, bar_id_1_c3_map_value_tm])
        bar_id_1_c4_tm = TypeMetadata(
            kind='struct',
            name='c4',
            key=
            'hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1/_inner_/c4',
            data_type='struct<c5:int,c6:int>',
            sort_order=3,
            children=[bar_id_1_c4_c5_tm, bar_id_1_c4_c6_tm])
        bar_id_1_struct_tm = TypeMetadata(
            kind='struct',
            name='_inner_',
            key=
            'hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1/_inner_',
            data_type='struct<c1:string,c2:array<string>,'
            'c3:map<string,string>,c4:struct<c5:int,c6:int>>',
            sort_order=0,
            children=[
                bar_id_1_c1_tm, bar_id_1_c2_tm, bar_id_1_c3_tm, bar_id_1_c4_tm
            ])
        bar_id_1_type_metadata = TypeMetadata(
            kind='array',
            name='bar_id_1',
            key='hive://gold.foo_schema/foo_table/bar_id_1/type/bar_id_1',
            data_type='array<struct<c1:string,c2:array<string>,'
            'c3:map<string,string>,c4:struct<c5:int,c6:int>>>',
            sort_order=0,
            children=[bar_id_1_struct_tm])
        return bar_id_1_type_metadata

    def _get_col_bar_id_2_expected_type_metadata(self) -> TypeMetadata:
        bar_id_2_c1_tm = TypeMetadata(
            kind='scalar',
            name='c1',
            key=
            'hive://gold.foo_schema/foo_table/bar_id_2/type/bar_id_2/_inner_/c1',
            description='String description',
            data_type='string',
            sort_order=0)
        bar_id_2_c2_tm = TypeMetadata(
            kind='array',
            name='c2',
            key=
            'hive://gold.foo_schema/foo_table/bar_id_2/type/bar_id_2/_inner_/c2',
            description='Array description',
            data_type='array<string>',
            sort_order=1,
            badges=[
                Badge(badge_name='primary key', category='column'),
                Badge(badge_name='pii', category='column')
            ])
        bar_id_2_struct_tm = TypeMetadata(
            kind='struct',
            name='_inner_',
            key=
            'hive://gold.foo_schema/foo_table/bar_id_2/type/bar_id_2/_inner_',
            data_type='struct<c1:string,c2:array<string>>',
            sort_order=0,
            children=[bar_id_2_c1_tm, bar_id_2_c2_tm])
        bar_id_2_type_metadata = TypeMetadata(
            kind='array',
            name='bar_id_2',
            key='hive://gold.foo_schema/foo_table/bar_id_2/type/bar_id_2',
            description='Array description',
            data_type='array<struct<c1:string,c2:array<string>>>',
            sort_order=0,
            children=[bar_id_2_struct_tm])
        return bar_id_2_type_metadata

    def tearDown(self) -> None:
        pass

    def test_health_nebula(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [None, None, None, None, None, None, None, None],
                    'row': [
                        '127.0.0.1', 9779, 19669, 'ONLINE', 100,
                        'amundsen:100',
                        'amundsen:100',
                        '3.1.0'
                    ]
                }],
                'columns': [
                    'Host', 'Port', 'HTTP port', 'Status', 'Leader count',
                    'Leader distribution', 'Partition distribution', 'Version'
                ],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            health_actual = nebula_proxy.health()
            expected_checks = {}
            health_expected = health_check.HealthCheck(status='ok', checks=expected_checks)
            self.assertEqual(health_actual.status, health_expected.status)
            self.assertDictEqual(health_actual.checks, health_expected.checks)

        # Test health failure (e.g. any other error)
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.side_effect = Exception()
            health_actual = nebula_proxy.health()
            expected_checks = {}
            health_expected = health_check.HealthCheck(status='fail', checks=expected_checks)
            self.assertEqual(health_actual.status, health_expected.status)
            self.assertDictEqual(health_actual.checks, health_expected.checks)

    def test_get_table(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.side_effect = [
                self.col_usage_return_value, self.table_usage_return_value,
                self.table_level_return_value, self.table_common_usage, []
            ]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            table = nebula_proxy.get_table(table_uri='dummy_uri')

            expected = Table(
                database='delta',
                cluster='gold',
                schema='test_schema',
                name='delta_test_table',
                key=None,
                tags=[
                    Tag(tag_type='default', tag_name='expensive'),
                    Tag(tag_type='default', tag_name='tag2'),
                    Tag(tag_type='default', tag_name='tag1'),
                    Tag(tag_type='default', tag_name='low_quality')
                ],
                badges=[Badge(badge_name='beta', category='table_status')],
                table_readers=[
                    Reader(user=User(user_id='roald.amundsen@example.org',
                                     email='roald.amundsen@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=500),
                    Reader(user=User(user_id='doald3@example.org',
                                     email='doald3@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=100),
                    Reader(user=User(user_id='hoald7@example.org',
                                     email='hoald7@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=100),
                    Reader(user=User(user_id='foald5@example.org',
                                     email='foald5@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=100),
                    Reader(user=User(user_id='aoald0@example.org',
                                     email='aoald0@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=100)
                ],
                description='test table for delta',
                columns=[
                    Column(
                        name='col1',
                        key=None,
                        description='col1 description',
                        col_type='bigint',
                        sort_order=1,
                        stats=[],
                        badges=[],
                        type_metadata=TypeMetadata(
                            kind='scalar',
                            name='col1',
                            key=
                            'delta://gold.test_schema/delta_test_table/col1/type/col1',
                            description=
                            'data_type: "bigint", kind: "scalar", name: "col1"',
                            data_type='bigint',
                            sort_order=0,
                            badges=[],
                            children=[])),
                    Column(
                        name='col2',
                        key=None,
                        description='col2 nested delta column',
                        col_type='struct<col3:string,col4:bigint>',
                        sort_order=2,
                        stats=[],
                        badges=[],
                        type_metadata=TypeMetadata(
                            kind='struct',
                            name='col2',
                            key=
                            'delta://gold.test_schema/delta_test_table/col2/type/col2',
                            description=None,
                            data_type='struct<col3:string,col4:bigint>',
                            sort_order=0,
                            badges=[],
                            children=[
                                TypeMetadata(
                                    kind='scalar',
                                    name='col3',
                                    key=
                                    'delta://gold.test_schema/delta_test_table/col2/type/col2/col3',
                                    description=None,
                                    data_type='string',
                                    sort_order=0,
                                    badges=[],
                                    children=[]),
                                TypeMetadata(
                                    kind='scalar',
                                    name='col4',
                                    key=
                                    'delta://gold.test_schema/delta_test_table/col2/type/col2/col4',
                                    description=None,
                                    data_type='bigint',
                                    sort_order=0,
                                    badges=[],
                                    children=[])
                            ]))
                ],
                owners=[
                    User(user_id='roald.amundsen@example.org',
                         email='roald.amundsen@example.org',
                         first_name=None,
                         last_name=None,
                         full_name=None,
                         display_name=None,
                         is_active=True,
                         github_username=None,
                         team_name=None,
                         slack_id=None,
                         employee_type=None,
                         manager_fullname=None,
                         manager_email=None,
                         manager_id=None,
                         role_name=None,
                         profile_url=None,
                         other_key_values={}),
                    User(user_id='chrisc@example.org',
                         email='chrisc@example.org',
                         first_name=None,
                         last_name=None,
                         full_name=None,
                         display_name=None,
                         is_active=True,
                         github_username=None,
                         team_name=None,
                         slack_id=None,
                         employee_type=None,
                         manager_fullname=None,
                         manager_email=None,
                         manager_id=None,
                         role_name=None,
                         profile_url=None,
                         other_key_values={})
                ],
                watermarks=[
                    Watermark(watermark_type='low_watermark',
                              partition_key='col3',
                              partition_value='2017-04-22/col4=0',
                              create_time='2019-10-01T12:13:14'),
                    Watermark(watermark_type='high_watermark',
                              partition_key='col3',
                              partition_value='2019-09-30/col4=11',
                              create_time='2019-10-01T12:13:14')
                ],
                table_writer=Application(
                    application_url=
                    'https://airflow_host.net/admin/airflow/tree?dag_id=event_test',
                    description=
                    'Airflow with id event_test/hive.test_schema.test_table1',
                    id=
                    'application://gold.airflow/event_test/hive.test_schema.test_table1',
                    name='Airflow',
                    kind='Producing'),
                table_apps=[
                    Application(
                        application_url=
                        'https://airflow_host.net/admin/airflow/tree?dag_id=event_test',
                        description=
                        'Airflow with id event_test/hive.test_schema.test_table1',
                        id=
                        'application://gold.airflow/event_test/hive.test_schema.test_table1',
                        name='Airflow',
                        kind='Producing')
                ],
                resource_reports=[
                    ResourceReport(
                        name='Advanced Profile',
                        url=
                        'https://pandas-profiling.github.io/pandas-profiling/examples/master/census/census_report.html'
                    )
                ],
                last_updated_timestamp=1570230473,
                source=Source(
                    source_type='github',
                    source='https://github.com/amundsen-io/amundsen/'),
                programmatic_descriptions=[
                    ProgrammaticDescription(
                        source='quality_service',
                        text=
                        '### Quality Report:\n--- \nIpsus enom. Ipsus enom ipsus lorenum.\n---\n[![Build Status](https://api.travis-ci.com/amundsen-io/amundsendatabuilder.svg?branch=master)](https://travis-ci.com/amundsen-io/amundsendatabuilder)'
                    ),
                    ProgrammaticDescription(
                        source='s3_crawler',
                        text='**Size**: 50T\n\n**Monthly Cost**: $5000')
                ],
                common_joins=[
                    SqlJoin(
                        column='col2',
                        joined_on_table=TableSummary(database='hive',
                                                     cluster='gold',
                                                     schema='test_schema',
                                                     name='test_table3',
                                                     description=None,
                                                     schema_description=None),
                        joined_on_column='col2',
                        join_type='inner join',
                        join_sql=
                        'SELECT * FROM test_table1 inner join test_table3 on test_table1.col2 = test_table3.col1 where test_table1.col5 > 10.0'
                    ),
                    SqlJoin(
                        column='col2',
                        joined_on_table=TableSummary(database='hive',
                                                     cluster='gold',
                                                     schema='test_schema',
                                                     name='test_table3',
                                                     description=None,
                                                     schema_description=None),
                        joined_on_column='col1',
                        join_type='inner join',
                        join_sql=
                        'SELECT * FROM test_table1 inner join test_table3 on test_table1.col2 = test_table3.col1 where test_table1.col5 > 10.0'
                    )
                ],
                common_filters=[
                    SqlWhere(where_clause='where test_table1.col5 > 10.0')
                ])

            self.assertEqual(str(expected), str(table))

    def test_get_table_view_only(self) -> None:
        col_usage_return_value = copy.deepcopy(self.col_usage_return_value)
        for col in col_usage_return_value[0]['data']:
            col['row'][3]['Table.is_view'] = True

        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.side_effect = [
                col_usage_return_value, self.table_usage_return_value,
                self.table_level_return_value, self.table_common_usage, []
            ]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            table = nebula_proxy.get_table(table_uri='dummy_uri')

            expected = Table(
                database='delta',
                cluster='gold',
                schema='test_schema',
                name='delta_test_table',
                key=None,
                tags=[
                    Tag(tag_type='default', tag_name='expensive'),
                    Tag(tag_type='default', tag_name='tag2'),
                    Tag(tag_type='default', tag_name='tag1'),
                    Tag(tag_type='default', tag_name='low_quality')
                ],
                badges=[Badge(badge_name='beta', category='table_status')],
                table_readers=[
                    Reader(user=User(user_id='roald.amundsen@example.org',
                                     email='roald.amundsen@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=500),
                    Reader(user=User(user_id='doald3@example.org',
                                     email='doald3@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=100),
                    Reader(user=User(user_id='hoald7@example.org',
                                     email='hoald7@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=100),
                    Reader(user=User(user_id='foald5@example.org',
                                     email='foald5@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=100),
                    Reader(user=User(user_id='aoald0@example.org',
                                     email='aoald0@example.org',
                                     first_name=None,
                                     last_name=None,
                                     full_name=None,
                                     display_name=None,
                                     is_active=True,
                                     github_username=None,
                                     team_name=None,
                                     slack_id=None,
                                     employee_type=None,
                                     manager_fullname=None,
                                     manager_email=None,
                                     manager_id=None,
                                     role_name=None,
                                     profile_url=None,
                                     other_key_values={}),
                           read_count=100)
                ],
                description='test table for delta',
                columns=[
                    Column(
                        name='col1',
                        key=None,
                        description='col1 description',
                        col_type='bigint',
                        sort_order=1,
                        stats=[],
                        badges=[],
                        type_metadata=TypeMetadata(
                            kind='scalar',
                            name='col1',
                            key=
                            'delta://gold.test_schema/delta_test_table/col1/type/col1',
                            description=
                            'data_type: "bigint", kind: "scalar", name: "col1"',
                            data_type='bigint',
                            sort_order=0,
                            badges=[],
                            children=[])),
                    Column(
                        name='col2',
                        key=None,
                        description='col2 nested delta column',
                        col_type='struct<col3:string,col4:bigint>',
                        sort_order=2,
                        stats=[],
                        badges=[],
                        type_metadata=TypeMetadata(
                            kind='struct',
                            name='col2',
                            key=
                            'delta://gold.test_schema/delta_test_table/col2/type/col2',
                            description=None,
                            data_type='struct<col3:string,col4:bigint>',
                            sort_order=0,
                            badges=[],
                            children=[
                                TypeMetadata(
                                    kind='scalar',
                                    name='col3',
                                    key=
                                    'delta://gold.test_schema/delta_test_table/col2/type/col2/col3',
                                    description=None,
                                    data_type='string',
                                    sort_order=0,
                                    badges=[],
                                    children=[]),
                                TypeMetadata(
                                    kind='scalar',
                                    name='col4',
                                    key=
                                    'delta://gold.test_schema/delta_test_table/col2/type/col2/col4',
                                    description=None,
                                    data_type='bigint',
                                    sort_order=0,
                                    badges=[],
                                    children=[])
                            ]))
                ],
                owners=[
                    User(user_id='roald.amundsen@example.org',
                         email='roald.amundsen@example.org',
                         first_name=None,
                         last_name=None,
                         full_name=None,
                         display_name=None,
                         is_active=True,
                         github_username=None,
                         team_name=None,
                         slack_id=None,
                         employee_type=None,
                         manager_fullname=None,
                         manager_email=None,
                         manager_id=None,
                         role_name=None,
                         profile_url=None,
                         other_key_values={}),
                    User(user_id='chrisc@example.org',
                         email='chrisc@example.org',
                         first_name=None,
                         last_name=None,
                         full_name=None,
                         display_name=None,
                         is_active=True,
                         github_username=None,
                         team_name=None,
                         slack_id=None,
                         employee_type=None,
                         manager_fullname=None,
                         manager_email=None,
                         manager_id=None,
                         role_name=None,
                         profile_url=None,
                         other_key_values={})
                ],
                watermarks=[
                    Watermark(watermark_type='low_watermark',
                              partition_key='col3',
                              partition_value='2017-04-22/col4=0',
                              create_time='2019-10-01T12:13:14'),
                    Watermark(watermark_type='high_watermark',
                              partition_key='col3',
                              partition_value='2019-09-30/col4=11',
                              create_time='2019-10-01T12:13:14')
                ],
                table_writer=Application(
                    application_url=
                    'https://airflow_host.net/admin/airflow/tree?dag_id=event_test',
                    description=
                    'Airflow with id event_test/hive.test_schema.test_table1',
                    id=
                    'application://gold.airflow/event_test/hive.test_schema.test_table1',
                    name='Airflow',
                    kind='Producing'),
                table_apps=[
                    Application(
                        application_url=
                        'https://airflow_host.net/admin/airflow/tree?dag_id=event_test',
                        description=
                        'Airflow with id event_test/hive.test_schema.test_table1',
                        id=
                        'application://gold.airflow/event_test/hive.test_schema.test_table1',
                        name='Airflow',
                        kind='Producing')
                ],
                resource_reports=[
                    ResourceReport(
                        name='Advanced Profile',
                        url=
                        'https://pandas-profiling.github.io/pandas-profiling/examples/master/census/census_report.html'
                    )
                ],
                last_updated_timestamp=1570230473,
                source=Source(
                    source_type='github',
                    source='https://github.com/amundsen-io/amundsen/'),
                is_view=True,
                programmatic_descriptions=[
                    ProgrammaticDescription(
                        source='quality_service',
                        text=
                        '### Quality Report:\n--- \nIpsus enom. Ipsus enom ipsus lorenum.\n---\n[![Build Status](https://api.travis-ci.com/amundsen-io/amundsendatabuilder.svg?branch=master)](https://travis-ci.com/amundsen-io/amundsendatabuilder)'
                    ),
                    ProgrammaticDescription(
                        source='s3_crawler',
                        text='**Size**: 50T\n\n**Monthly Cost**: $5000')
                ],
                common_joins=[
                    SqlJoin(
                        column='col2',
                        joined_on_table=TableSummary(database='hive',
                                                     cluster='gold',
                                                     schema='test_schema',
                                                     name='test_table3',
                                                     description=None,
                                                     schema_description=None),
                        joined_on_column='col2',
                        join_type='inner join',
                        join_sql=
                        'SELECT * FROM test_table1 inner join test_table3 on test_table1.col2 = test_table3.col1 where test_table1.col5 > 10.0'
                    ),
                    SqlJoin(
                        column='col2',
                        joined_on_table=TableSummary(database='hive',
                                                     cluster='gold',
                                                     schema='test_schema',
                                                     name='test_table3',
                                                     description=None,
                                                     schema_description=None),
                        joined_on_column='col1',
                        join_type='inner join',
                        join_sql=
                        'SELECT * FROM test_table1 inner join test_table3 on test_table1.col2 = test_table3.col1 where test_table1.col5 > 10.0'
                    )
                ],
                common_filters=[
                    SqlWhere(where_clause='where test_table1.col5 > 10.0')
                ])

            self.assertEqual(str(expected), str(table))

    def test_get_table_with_valid_description(self) -> None:
        """
        Test description is returned for table
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [None],
                    'row': ['sample description']
                }],
                'columns': ['description'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            table_description = nebula_proxy.get_table_description(
                table_uri='test_table')

            table_description_query = Template(
                textwrap.dedent("""
            MATCH (n:`Table`)-[:DESCRIPTION]->(d:Description)
            WHERE id(n) == "{{ vid }}"
            RETURN d.Description.description AS description;
            """))
            mock_execute.assert_called_with(
                query=table_description_query.render(vid='test_table'),
                param_dict={})

            self.assertEqual(table_description, 'sample description')

    def test_get_table_with_no_description(self) -> None:
        """
        Test None is returned for table with no description
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName': 'amundsen',
                'data': [],
                'columns': ['description'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            table_description = nebula_proxy.get_table_description(
                table_uri='test_table')

            table_description_query = Template(
                textwrap.dedent("""
            MATCH (n:`Table`)-[:DESCRIPTION]->(d:Description)
            WHERE id(n) == "{{ vid }}"
            RETURN d.Description.description AS description;
            """))
            mock_execute.assert_called_with(
                query=table_description_query.render(vid='test_table'),
                param_dict={})

            self.assertIsNone(table_description)

    def test_put_table_description(self) -> None:
        """
        Test updating table description
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.put_table_description(table_uri='test_table',
                                               description='test_description')

            self.assertEqual(mock_execute.call_count, 1)

    def test_get_column_with_valid_description(self) -> None:
        """
        Test description is returned for column
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [None],
                    'row': ['sample description']
                }],
                'columns': ['description'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            col_description = nebula_proxy.get_column_description(
                table_uri='test_table', column_name='test_column')
            column_description_query = Template(
                textwrap.dedent("""
            MATCH (tbl:Table)-[:COLUMN]->(c:Column)-[:DESCRIPTION]->(d:Description)
            WHERE id(tbl) == "{{ vid }}" AND id(c) == "{{ vid }}/{{ column_name }}"
            RETURN d.Description.description AS description;
            """))

            mock_execute.assert_called_with(
                query=column_description_query.render(
                    vid="test_table", column_name="test_column"),
                param_dict={})

            self.assertEqual(col_description, 'sample description')

    def test_get_column_with_no_description(self) -> None:
        """
        Test None is returned for column with no description
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName': 'amundsen',
                'data': [],
                'columns': ['description'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            col_description = nebula_proxy.get_column_description(
                table_uri='test_table', column_name='test_column')
            column_description_query = Template(
                textwrap.dedent("""
            MATCH (tbl:Table)-[:COLUMN]->(c:Column)-[:DESCRIPTION]->(d:Description)
            WHERE id(tbl) == "{{ vid }}" AND id(c) == "{{ vid }}/{{ column_name }}"
            RETURN d.Description.description AS description;
            """))

            mock_execute.assert_called_with(
                query=column_description_query.render(
                    vid="test_table", column_name="test_column"),
                param_dict={})

            self.assertIsNone(col_description)

    def test_put_column_description(self) -> None:
        """
        Test updating column description
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.put_column_description(table_uri='test_table',
                                                column_name='test_column',
                                                description='test_description')

            self.assertEqual(mock_execute.call_count, 1)

    def test_get_type_metadata_with_valid_description(self) -> None:
        """
        Test description is returned for type_metadata
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [None],
                    'row': ['sample description']
                }],
                'columns': ['description'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            col_description = nebula_proxy.get_type_metadata_description(
                type_metadata_key='test_table/test_column'
                '/test_type_metadata')
            type_metadata_description_query = Template(
                textwrap.dedent("""
            MATCH (n:`Type_Metadata`)-[:DESCRIPTION]->(d:Description)
            WHERE id(n) == "{{ vid }}"
            RETURN d.Description.description AS description;
            """))
            mock_execute.assert_called_with(
                query=type_metadata_description_query.render(
                    vid='test_table/test_column/test_type_metadata'),
                param_dict={})

            self.assertEqual(col_description, 'sample description')

    def test_get_type_metadata_with_no_description(self) -> None:
        """
        Test None is returned for type_metadata with no description
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName': 'amundsen',
                'data': [],
                'columns': ['description'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            col_description = nebula_proxy.get_type_metadata_description(
                type_metadata_key='test_table/test_column'
                '/test_type_metadata')
            type_metadata_description_query = Template(
                textwrap.dedent("""
            MATCH (n:`Type_Metadata`)-[:DESCRIPTION]->(d:Description)
            WHERE id(n) == "{{ vid }}"
            RETURN d.Description.description AS description;
            """))
            mock_execute.assert_called_with(
                query=type_metadata_description_query.render(
                    vid='test_table/test_column/test_type_metadata'),
                param_dict={})

            self.assertIsNone(col_description)

    def test_put_type_metadata_description(self) -> None:
        """
        Test updating type_metadata description
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.put_type_metadata_description(
                type_metadata_key='test_table/test_column/test_type_metadata',
                description='test_description')

            self.assertEqual(mock_execute.call_count, 1)

    def test_add_owner(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.add_owner(table_uri='dummy_uri', owner='tester')

            self.assertEqual(mock_execute.call_count, 1)

    def test_delete_owner(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.delete_owner(table_uri='dummy_uri', owner='tester')
            self.assertEqual(mock_execute.call_count, 1)

    def test_add_table_badge(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.add_badge(id='dummy_uri',
                                   badge_name='hive',
                                   resource_type=ResourceType.Table)
            self.assertEqual(mock_execute.call_count, 1)

    def test_add_column_badge(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.add_badge(id='dummy_uri',
                                   badge_name='hive',
                                   resource_type=ResourceType.Column)
            self.assertEqual(mock_execute.call_count, 1)

    def test_add_type_metadata_badge(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.add_badge(id='dummy_uri',
                                   badge_name='hive',
                                   resource_type=ResourceType.Type_Metadata)
            self.assertEqual(mock_execute.call_count, 1)

    def test_add_tag(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.add_tag(id='dummy_uri', tag='hive')
            self.assertEqual(mock_execute.call_count, 1)

    def test_delete_tag(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.delete_tag(id='dummy_uri', tag='hive')
            self.assertEqual(mock_execute.call_count, 1)
            nebula_proxy.delete_tag(id='dummy_uri', tag='hive')

    def test_get_tags(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [{
                        'type': 'vertex',
                        'id': 'needs_documentation'
                    }, None],
                    'row': [{
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649259854
                    }, 2]
                }, {
                    'meta': [{
                        'type': 'vertex',
                        'id': 'recommended'
                    }, None],
                    'row': [{
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649259854
                    }, 1]
                }, {
                    'meta': [{
                        'type': 'vertex',
                        'id': 'tag2'
                    }, None],
                    'row': [{
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649259854
                    }, 2]
                }, {
                    'meta': [{
                        'type': 'vertex',
                        'id': 'tag1'
                    }, None],
                    'row': [{
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649259854
                    }, 3]
                }, {
                    'meta': [{
                        'type': 'vertex',
                        'id': 'cheap'
                    }, None],
                    'row': [{
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649237215
                    }, 1]
                }, {
                    'meta': [{
                        'type': 'vertex',
                        'id': 'expensive'
                    }, None],
                    'row': [{
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649237215
                    }, 1]
                }, {
                    'meta': [{
                        'type': 'vertex',
                        'id': 'low_quality'
                    }, None],
                    'row': [{
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649237215
                    }, 1]
                }, {
                    'meta': [{
                        'type': 'vertex',
                        'id': 'delta'
                    }, None],
                    'row': [{
                        'Tag.tag_type': 'default',
                        'Tag.published_tag': 'unique_tag',
                        'Tag.publisher_last_updated_epoch_ms': 1649259854
                    }, 1]
                }],
                'columns': ['tag_name', 'tag_count'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            actual = nebula_proxy.get_tags()

            expected = [
                TagDetail(tag_name='needs_documentation', tag_count=2),
                TagDetail(tag_name='recommended', tag_count=1),
                TagDetail(tag_name='tag2', tag_count=2),
                TagDetail(tag_name='tag1', tag_count=3),
                TagDetail(tag_name='cheap', tag_count=1),
                TagDetail(tag_name='expensive', tag_count=1),
                TagDetail(tag_name='low_quality', tag_count=1),
                TagDetail(tag_name='delta', tag_count=1)
            ]

            self.assertEqual(actual.__repr__(), expected.__repr__())

    def test_get_nebula_latest_updated_ts(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [{
                        'type': 'vertex',
                        'id': 'amundsen_updated_timestamp'
                    }],
                    'row': [{
                        'Updatedtimestamp.published_tag':
                        'unique_tag',
                        'Updatedtimestamp.publisher_last_updated_epoch_ms':
                        1000,
                        'Updatedtimestamp.latest_timestamp':
                        1000
                    }]
                }],
                'columns': ['n'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_last_updated_ts = nebula_proxy.get_latest_updated_ts()
            self.assertEqual(nebula_last_updated_ts, 1000)

            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [{
                        'type': 'vertex',
                        'id': 'amundsen_updated_timestamp'
                    }],
                    'row': [{
                        'Updatedtimestamp.published_tag':
                        'unique_tag',
                        'Updatedtimestamp.publisher_last_updated_epoch_ms':
                        None,
                        'Updatedtimestamp.latest_timestamp':
                        None
                    }]
                }],
                'columns': ['n'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_last_updated_ts = nebula_proxy.get_latest_updated_ts()
            self.assertEqual(nebula_last_updated_ts, 0)

            mock_execute.return_value = [{
                'spaceName': 'amundsen',
                'data': [],
                'columns': ['n'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_last_updated_ts = nebula_proxy.get_latest_updated_ts()
            self.assertIsNone(nebula_last_updated_ts)

    def test_get_statistics(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [None, None, None, None, None, None],
                    'row': [6, 6, 13, 4, 2, 4]
                }],
                'columns': [
                    'number_of_tables', 'number_of_documented_tables',
                    'number_of_documented_cols', 'number_of_owners',
                    'number_of_tables_with_owners',
                    'number_of_documented_and_owned_tables'
                ],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_statistics = nebula_proxy.get_statistics()
            self.assertEqual(
                nebula_statistics, {
                    'number_of_tables': 6,
                    'number_of_documented_tables': 6,
                    'number_of_documented_cols': 13,
                    'number_of_owners': 4,
                    'number_of_tables_with_owners': 2,
                    'number_of_documented_and_owned_tables': 4
                })

    def test_get_popular_tables(self) -> None:
        # Test cache hit for global popular tables
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [None, None],
                    'row': ["foo", 6]
                }, {
                    'meta': [None, None],
                    'row': ["bar", 16]
                }],
                'columns': ['vid', 'score'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            self.assertEqual(nebula_proxy._get_global_popular_resources_uris(2), ['foo', 'bar'])
            self.assertEqual(nebula_proxy._get_global_popular_resources_uris(2), ['foo', 'bar'])
            self.assertEqual(nebula_proxy._get_global_popular_resources_uris(2), ['foo', 'bar'])

            self.assertEqual(mock_execute.call_count, 1)

        # Test cache hit for personal popular tables
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [None, None],
                    'row': ["foo", 6]
                }, {
                    'meta': [None, None],
                    'row': ["bar", 16]
                }],
                'columns': ['vid', 'score'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            self.assertEqual(nebula_proxy._get_personal_popular_resources_uris(2, 'test_id'), ['foo', 'bar'])
            self.assertEqual(nebula_proxy._get_personal_popular_resources_uris(2, 'test_id'), ['foo', 'bar'])
            self.assertEqual(nebula_proxy._get_personal_popular_resources_uris(2, 'other_id'), ['foo', 'bar'])

            self.assertEqual(mock_execute.call_count, 2)

        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [None, None, None, None, None],
                    'row': ['db', 'clstr', 'sch', 'foo', 'test description']
                }, {
                    'meta': [None, None, None, None, None],
                    'row': ['db', 'clstr', 'sch', 'bar', None]
                }],
                'columns': [
                    'database_name', 'cluster_name', 'schema_name',
                    'table_name', 'table_description'
                ],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            actual = nebula_proxy.get_popular_tables(num_entries=2)

            expected = [
                PopularTable(database='db', cluster='clstr', schema='sch', name='foo', description='test description'),
                PopularTable(database='db', cluster='clstr', schema='sch', name='bar'),
            ]
            print(actual)

            self.assertEqual(actual.__repr__(), expected.__repr__())

    def test_get_popular_resources_table(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_get_global_popular_resources_uris') as mock_uris, patch.object(NebulaProxy, '_get_popular_tables') as mock_execute:
            mock_execute.return_value = [
                TableSummary(**{'database': 'db', 'cluster': 'clstr', 'schema': 'sch', 'name': 'foo',
                                'description': 'test description'}),
                TableSummary(**{'database': 'db', 'cluster': 'clstr', 'schema': 'sch', 'name': 'bar'})
            ]
            mock_uris.return_value = ['foo', 'bar']

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            actual = nebula_proxy.get_popular_resources(num_entries=2, resource_types=["table"])

            expected = {
                ResourceType.Table.name: [
                    TableSummary(database='db', cluster='clstr', schema='sch', name='foo',
                                 description='test description'),
                    TableSummary(database='db', cluster='clstr', schema='sch', name='bar')
                ]
            }

            self.assertEqual(expected.__repr__(), actual.__repr__())

    def test_get_popular_resources_table_dashboard(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_get_global_popular_resources_uris'
        ) as mock_uris, patch.object(
                NebulaProxy, '_get_popular_tables') as mock_tbl, patch.object(
                    NebulaProxy, '_get_popular_dashboards') as mock_dash:
            mock_tbl.return_value = [
                TableSummary(
                    **{
                        'database': 'db',
                        'cluster': 'clstr',
                        'schema': 'sch',
                        'name': 'foo',
                        'description': 'test description'
                    })
            ]
            mock_dash.return_value = [
                DashboardSummary(
                    **{
                        'uri': 'dashboard',
                        'cluster': 'clstr',
                        'group_name': 'gn',
                        'group_url': 'gu',
                        'product': 'product',
                        'name': 'bar',
                        'url': 'url',
                        'description': 'desc'
                    })
            ]
            mock_uris.return_value = ['foo', 'bar']

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            actual = nebula_proxy.get_popular_resources(num_entries=2, resource_types=["table", "dashboard"])

            expected = {
                ResourceType.Table.name: [
                    TableSummary(database='db',
                                 cluster='clstr',
                                 schema='sch',
                                 name='foo',
                                 description='test description',
                                 schema_description=None)
                ],
                ResourceType.Dashboard.name: [
                    DashboardSummary(uri='dashboard',
                                     cluster='clstr',
                                     group_name='gn',
                                     group_url='gu',
                                     product='product',
                                     name='bar',
                                     url='url',
                                     description='desc',
                                     last_successful_run_timestamp=None,
                                     chart_names=[])
                ]
            }

            self.assertEqual(expected.__repr__(), actual.__repr__())

    def test_get_user(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [{
                        'type': 'vertex',
                        'id': 'test_email'
                    }, None],
                    'row': [{
                        'User.is_active': True,
                        'User.profile_url': None,
                        'User.employee_type': None,
                        'User.updated_at': None,
                        'User.last_name': None,
                        'User.slack_id': None,
                        'User.role_name': None,
                        'User.team_name': None,
                        'User.full_name': None,
                        'User.first_name': None,
                        'User.publisher_last_updated_epoch_ms': 1649237216,
                        'User.github_username': None,
                        'User.manager_fullname': '',
                        'User.user_id': '',
                        'User.email': 'test_email',
                        'User.published_tag': 'unique_tag'
                    }, None]
                }],
                'columns': ['user_record', 'manager_record'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            nebula_user = nebula_proxy.get_user(id='test_email')
            self.assertEqual(nebula_user.email, 'test_email')

    def test_get_user_other_key_values(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [{
                        'type': 'vertex',
                        'id': 'test_email'
                    }, None],
                    'row': [{
                        'User.is_active': True,
                        'User.profile_url': None,
                        'User.employee_type': None,
                        'User.updated_at': None,
                        'User.last_name': None,
                        'User.slack_id': None,
                        'User.role_name': None,
                        'User.team_name': None,
                        'User.full_name': None,
                        'User.first_name': None,
                        'User.publisher_last_updated_epoch_ms': 1649237216,
                        'User.github_username': None,
                        'User.manager_fullname': '',
                        'User.mode_user_id': 'mode_foo_bar',
                        'User.email': 'test_email',
                        'User.published_tag': 'unique_tag'
                    }, None]
                }],
                'columns': ['user_record', 'manager_record'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            nebula_user = nebula_proxy.get_user(id='test_email')
            self.assertEqual(nebula_user.other_key_values, {'mode_user_id': 'mode_foo_bar'})

    def test_put_user_new_user(self) -> None:
        """
        Test creating a new user
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.side_effect = [
                [{
                    'spaceName': 'amundsen',
                    'data': [],
                    'columns': ['u'],
                    'errors': {
                        'code': 0
                    },
                    'latencyInUs': 1
                }], [{}],
                [{
                    'spaceName':
                    'amundsen',
                    'data': [{
                        'meta': [{
                            'type': 'vertex',
                            'id': 'test_email'
                        }],
                        'row': [{
                            'User.is_active': True,
                            'User.profile_url': None,
                            'User.employee_type': None,
                            'User.updated_at': None,
                            'User.last_name': None,
                            'User.slack_id': None,
                            'User.role_name': None,
                            'User.team_name': None,
                            'User.full_name': None,
                            'User.first_name': None,
                            'User.publisher_last_updated_epoch_ms': 1649237216,
                            'User.github_username': None,
                            'User.manager_fullname': '',
                            'User.user_id': '',
                            'User.email': 'test_email',
                            'User.published_tag': 'unique_tag'
                        }]
                    }],
                    'columns': ['u'],
                    'errors': {
                        'code': 0
                    },
                    'latencyInUs': 1
                }]
            ]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            test_user = MagicMock()
            nebula_proxy.create_update_user(user=test_user)

            self.assertEqual(mock_execute.call_count, 3)

    def test_get_users(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            test_user_obj = UserModel(email='test_email',
                                      first_name='test_first_name',
                                      last_name='test_last_name',
                                      full_name='test_full_name',
                                      is_active=True,
                                      profile_url='test_profile',
                                      github_username='test-github',
                                      team_name='test_team',
                                      slack_id='test_id',
                                      employee_type='teamMember',
                                      manager_fullname='test_manager')

            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [[{
                        'type': 'vertex',
                        'id': 'test_email'
                    }]],
                    'row': [[{
                        'User.is_active': True,
                        'User.profile_url': 'test_profile',
                        'User.employee_type': 'teamMember',
                        'User.updated_at': None,
                        'User.last_name': 'test_last_name',
                        'User.slack_id': 'test_id',
                        'User.role_name': None,
                        'User.team_name': 'test_team',
                        'User.full_name': 'test_full_name',
                        'User.first_name': 'test_first_name',
                        'User.publisher_last_updated_epoch_ms': 1649237216,
                        'User.github_username': 'test-github',
                        'User.manager_fullname': 'test_manager',
                        'User.user_id': '',
                        'User.email': 'test_email',
                        'User.published_tag': 'unique_tag'
                    }]]
                }],
                'columns': ['users'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            users = nebula_proxy.get_users()
            actual_data = [test_user_obj]
            for attr in [
                    'employee_type', 'full_name', 'is_active', 'profile_url',
                    'github_username', 'slack_id', 'last_name', 'first_name',
                    'team_name', 'email', 'manager_fullname'
            ]:
                self.assertEqual(getattr(users[0], attr),
                                 getattr(actual_data[0], attr))

    def test_get_table_by_user_relation(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [{
                        'type': 'vertex',
                        'id': 'database://hive'
                    }, {
                        'type': 'vertex',
                        'id': 'db_name://cluster'
                    }, {
                        'type': 'vertex',
                        'id': 'db_name://cluster.schema'
                    }, {
                        'type': 'vertex',
                        'id': 'db_name://cluster.schema/table_name'
                    }, {
                        'type':
                        'vertex',
                        'id':
                        'db_name://cluster.schema/table_name/_description'
                    }],
                    'row': [{
                        'Database.name':
                        'db_name',
                        'Database.published_tag':
                        'unique_tag',
                        'Database.publisher_last_updated_epoch_ms':
                        1649259854
                    }, {
                        'Cluster.name': 'cluster',
                        'Cluster.publisher_last_updated_epoch_ms': 1649259854,
                        'Cluster.published_tag': 'unique_tag'
                    }, {
                        'Schema.name': 'schema',
                        'Schema.publisher_last_updated_epoch_ms': 1649259854,
                        'Schema.published_tag': 'unique_tag'
                    }, {
                        'Table.publisher_last_updated_epoch_ms': 1649259854,
                        'Table.published_tag': 'unique_tag',
                        'Table.name': 'table_name',
                        'Table.is_view': True
                    }, {
                        'Description.published_tag': 'unique_tag',
                        'Description.publisher_last_updated_epoch_ms':
                        1649259854,
                        'Description.description_source': 'description',
                        'Description.description': '1st test table'
                    }]
                }],
                'columns': ['db', 'clstr', 'schema', 'resource', 'tbl_dscrpt'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            result = nebula_proxy.get_table_by_user_relation(user_email='test_user',
                                                            relation_type=UserResourceRel.follow)
            self.assertEqual(len(result['table']), 1)
            self.assertEqual(result['table'][0].name, 'table_name')
            self.assertEqual(result['table'][0].database, 'db_name')
            self.assertEqual(result['table'][0].cluster, 'cluster')
            self.assertEqual(result['table'][0].schema, 'schema')

    def test_get_dashboard_by_user_relation(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta':
                    [None, None, None, None, None, None, None, None, None],
                    'row': [
                        'cluster', 'dashboard_group', 'http://foo.bar/group',
                        'dashboard_uri', 'dashboard',
                        'http://foo.bar/dashboard', 'foobar', 'description',
                        1234567890
                    ]
                }],
                'columns': [
                    'cluster_name', 'dg_name', 'dg_url', 'uri', 'name', 'url',
                    'product', 'description', 'last_successful_run_timestamp'
                ],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            result = nebula_proxy.get_dashboard_by_user_relation(user_email='test_user',
                                                                relation_type=UserResourceRel.follow)

            expected = DashboardSummary(uri='dashboard_uri',
                                        cluster='cluster',
                                        group_name='dashboard_group',
                                        group_url='http://foo.bar/group',
                                        product='foobar',
                                        name='dashboard',
                                        url='http://foo.bar/dashboard',
                                        description='description',
                                        last_successful_run_timestamp=1234567890)

            self.assertEqual(len(result['dashboard']), 1)
            self.assertEqual(expected, result['dashboard'][0])

    def test_add_resource_relation_by_user(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.add_resource_relation_by_user(id='dummy_uri',
                                                      user_id='tester',
                                                      relation_type=UserResourceRel.follow,
                                                      resource_type=ResourceType.Table)
            self.assertEqual(mock_execute.call_count, 1)

    def test_delete_resource_relation_by_user(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.delete_resource_relation_by_user(id='dummy_uri',
                                                         user_id='tester',
                                                         relation_type=UserResourceRel.follow,
                                                         resource_type=ResourceType.Table)
            self.assertEqual(mock_execute.call_count, 1)


    def test_get_invalid_user(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [],
                'columns': ['user_record', 'manager_record'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            self.assertRaises(NotFoundException, nebula_proxy.get_user, id='invalid_email')

    def test_get_dashboard(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.side_effect = [
                [{'spaceName': 'amundsen',
            'data': [{'meta': [None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            [{'type': 'vertex', 'id': 'roald.amundsen@example.org'}],
            [],
            [],
            None,
            [[None, None, None], [None, None, None]],
            [{'type': 'vertex',
            'id': 'mode_dashboard://gold.test_group_id_1/test_dashboard_id_1/query/query_101/chart/chart_101'}],
            [[None, None, None, None, None]]],
            'row': ['gold',
            'mode_dashboard://gold.test_group_id_1/test_dashboard_id_1',
            'http://mode.test_group_id_1.com/test_dashboard_id_1',
            'test dashboard',
            'mode',
            '1592333799',
            None,
            'test group1',
            'http://mode.test_group_id_1.com',
            None,
            None,
            None,
            1592351454,
            [{'User.is_active': True,
            'User.profile_url': '',
            'User.employee_type': 'sailor',
            'User.updated_at': 0,
            'User.last_name': 'Amundsen',
            'User.slack_id': 'ramundzn',
            'User.role_name': 'swe',
            'User.team_name': 'Team Amundsen',
            'User.full_name': 'Roald Amundsen',
            'User.first_name': 'Roald',
            'User.publisher_last_updated_epoch_ms': 1649237216,
            'User.github_username': 'amundsen-io',
            'User.manager_fullname': '',
            'User.user_id': '',
            'User.email': 'roald.amundsen@example.org',
            'User.published_tag': 'unique_tag'}],
            [],
            [],
            100,
            [{'name': None, 'query_text': None, 'url': None},
            {'name': None, 'query_text': None, 'url': None}],
            [{'Chart.published_tag': 'unique_tag',
            'Chart.url': 'http://mode.test_group_id_1.com/test_dashboard_id_1/query/query_101/chart/chart_101',
            'Chart.name': 'chart_101',
            'Chart.id': 'chart_101',
            'Chart.type': 'chart_type_1',
            'Chart.publisher_last_updated_epoch_ms': 1649237249}],
            [{'name': 'test_table1',
            'schema': 'test_schema',
            'description': '1st test table',
            'cluster': 'gold',
            'database': 'hive'}]]}],
            'columns': ['cluster_name',
            'uri',
            'url',
            'name',
            'product',
            'created_timestamp',
            'description',
            'group_name',
            'group_url',
            'last_successful_run_timestamp',
            'last_run_timestamp',
            'last_run_state',
            'updated_timestamp',
            'owners',
            'tags',
            'badges',
            'recent_view_count',
            'queries',
            'charts',
            'tables'],
            'errors': {'code': 0},
            'latencyInUs': 1}],
                [{'spaceName': 'amundsen',
            'data': [{'meta': [None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            [],
            [],
            [],
            None,
            [[None, None, None]],
            [],
            [[None, None, None, None, None]]],
            'row': ['gold',
            'superset_dashboard://gold.test_group_id_3/test_dashboard_id_3',
            'http://mode.test_group_id_3.com/test_dashboard_id_3',
            'test dashboard',
            'superset',
            '1591333799',
            None,
            'test group3',
            'http://mode.test_group_id_3.com',
            None,
            None,
            None,
            None,
            [],
            [],
            [],
            0,
            [{'name': None, 'query_text': None, 'url': None}],
            [],
            [{'name': None,
            'schema': None,
            'description': None,
            'cluster': None,
            'database': None}]]}],
            'columns': ['cluster_name',
            'uri',
            'url',
            'name',
            'product',
            'created_timestamp',
            'description',
            'group_name',
            'group_url',
            'last_successful_run_timestamp',
            'last_run_timestamp',
            'last_run_state',
            'updated_timestamp',
            'owners',
            'tags',
            'badges',
            'recent_view_count',
            'queries',
            'charts',
            'tables'],
            'errors': {'code': 0},
            'latencyInUs': 1}]
            ]
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            dashboard = nebula_proxy.get_dashboard(id='dashboard_id')
            expected = DashboardDetail(
                uri='mode_dashboard://gold.test_group_id_1/test_dashboard_id_1',
                cluster='gold',
                group_name='test group1',
                group_url='http://mode.test_group_id_1.com',
                product='mode',
                name='test dashboard',
                url='http://mode.test_group_id_1.com/test_dashboard_id_1',
                description=None,
                created_timestamp=1592333799,
                updated_timestamp=1592351454,
                last_successful_run_timestamp=None,
                last_run_timestamp=None,
                last_run_state=None,
                owners=[
                    User(user_id='',
                         email='roald.amundsen@example.org',
                         first_name='Roald',
                         last_name='Amundsen',
                         full_name='Roald Amundsen',
                         display_name=None,
                         is_active=True,
                         github_username='amundsen-io',
                         team_name='Team Amundsen',
                         slack_id='ramundzn',
                         employee_type='sailor',
                         manager_fullname='',
                         manager_email=None,
                         manager_id=None,
                         role_name='swe',
                         profile_url='',
                         other_key_values={})
                ],
                frequent_users=[],
                chart_names=['chart_101'],
                query_names=None,
                queries=None,
                tables=[
                    PopularTable(database='hive',
                                 cluster='gold',
                                 schema='test_schema',
                                 name='test_table1',
                                 description='1st test table')
                ],
                tags=None,
                badges=None,
                recent_view_count=100)


            self.assertEqual(expected, dashboard)

            dashboard2 = nebula_proxy.get_dashboard(id='dashboard_id')

            expected2 = DashboardDetail(
                uri=
                'superset_dashboard://gold.test_group_id_3/test_dashboard_id_3',
                cluster='gold',
                group_name='test group3',
                group_url='http://mode.test_group_id_3.com',
                product='superset',
                name='test dashboard',
                url='http://mode.test_group_id_3.com/test_dashboard_id_3',
                description=None,
                created_timestamp=1591333799,
                updated_timestamp=None,
                last_successful_run_timestamp=None,
                last_run_timestamp=None,
                last_run_state=None,
                owners=None,
                frequent_users=[],
                chart_names=None,
                query_names=None,
                queries=None,
                tables=None,
                tags=None,
                badges=None,
                recent_view_count=None)

            self.assertEqual(expected2, dashboard2)

    def test_get_dashboard_with_valid_description(self) -> None:
        """
        Test description is returned for dashboard
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [None],
                    'row': ['sample description']
                }],
                'columns': ['description'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            table_description = nebula_proxy.get_dashboard_description(id='test_dashboard')

            dashboard_description_query = Template(
                textwrap.dedent("""
            MATCH (n:`Dashboard`)-[:DESCRIPTION]->(d:Description)
            WHERE id(n) == "{{ vid }}"
            RETURN d.Description.description AS description;
            """))
            mock_execute.assert_called_with(
                query=dashboard_description_query.render(
                    vid='test_dashboard'),
                param_dict={})

            self.assertEqual(table_description.description, 'sample description')

    def test_get_dashboard_with_no_description(self) -> None:
        """
        Test None is returned for table with no description
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [],
                'columns': ['description'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            table_description = nebula_proxy.get_dashboard_description(id='test_dashboard')

            dashboard_description_query = Template(
                textwrap.dedent("""
            MATCH (n:`Dashboard`)-[:DESCRIPTION]->(d:Description)
            WHERE id(n) == "{{ vid }}"
            RETURN d.Description.description AS description;
            """))
            mock_execute.assert_called_with(
                query=dashboard_description_query.render(
                    vid='test_dashboard'),
                param_dict={})
            self.assertIsNone(table_description.description)

    def test_put_dashboard_description(self) -> None:
        """
        Test updating table description
        :return:
        """
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            nebula_proxy.put_dashboard_description(
                id='test_dashboard', description='test_description')

            self.assertEqual(mock_execute.call_count, 1)

    def test_user_resource_relation_clause(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'):
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')
            actual = nebula_proxy._get_user_resource_relationship_clause(
                UserResourceRel.follow,
                id='foo',
                user_id='bar',
                resource_type=ResourceType.Table)
            expected = (
                '(resource:Table)-[r1:FOLLOWED_BY]->(usr:`User`)-[r2:FOLLOW]->(resource:Table)',
                'WHERE id(resource) == "foo" AND id(usr) == "bar" ')
            self.assertEqual(expected, actual)

            actual = nebula_proxy._get_user_resource_relationship_clause(
                UserResourceRel.read,
                id='foo',
                user_id='bar',
                resource_type=ResourceType.Table)
            expected = (
                '(resource:Table)-[r1:READ_BY]->(usr:`User`)-[r2:READ]->(resource:Table)',
                'WHERE id(resource) == "foo" AND id(usr) == "bar" ')
            self.assertEqual(expected, actual)

            actual = nebula_proxy._get_user_resource_relationship_clause(
                UserResourceRel.own,
                id='foo',
                user_id='bar',
                resource_type=ResourceType.Table)
            expected = (
                '(resource:Table)-[r1:OWNER]->(usr:`User`)-[r2:OWNER_OF]->(resource:Table)',
                'WHERE id(resource) == "foo" AND id(usr) == "bar" ')
            self.assertEqual(expected, actual)

            actual = nebula_proxy._get_user_resource_relationship_clause(
                UserResourceRel.follow,
                id='foo',
                user_id='bar',
                resource_type=ResourceType.Dashboard)
            expected = (
                '(resource:Dashboard)-[r1:FOLLOWED_BY]->(usr:`User`)-[r2:FOLLOW]->(resource:Dashboard)',
                'WHERE id(resource) == "foo" AND id(usr) == "bar" ')
            self.assertEqual(expected, actual)

    def test_get_lineage_no_lineage_information(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            key = "alpha"
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [[], []],
                    'row': [[], []]
                }],
                'columns': ['downstream_entities', 'upstream_entities'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            expected = Lineage(
                key=key,
                upstream_entities=[],
                downstream_entities=[],
                direction="both",
                depth=1
            )

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            actual = nebula_proxy.get_lineage(id=key, resource_type=ResourceType.Table, direction="both", depth=1)
            self.assertEqual(expected, actual)

    def test_get_lineage_success(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            key = "alpha"
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [[[None, None, [], None, None, None],
                              [None, None, [], None, None, None]],
                             [[None, None, [], None, None, None]]],
                    'row': [[{
                        'level': 1,
                        'source': 'hive',
                        'key': "hive://gold.test_schema/test's_table4",
                        'badges': [],
                        'usage': 0,
                        'parent': 'dynamo://gold.test_schema/test_table2'
                    }, {
                        'level': 1,
                        'source': 'hive',
                        'key': 'hive://gold.test_schema/test_table3',
                        'badges': [],
                        'usage': 0,
                        'parent': 'dynamo://gold.test_schema/test_table2'
                    }],
                            [{
                                'level': 1,
                                'source': 'hive',
                                'key': 'hive://gold.test_schema/test_table1',
                                'badges': [],
                                'usage': 1330,
                                'parent':
                                'dynamo://gold.test_schema/test_table2'
                            }]]
                }],
                'columns': ['downstream_entities', 'upstream_entities'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            expected = Lineage(
                key='alpha',
                direction='both',
                depth=4,
                upstream_entities=[
                    LineageItem(key='hive://gold.test_schema/test_table1',
                                level=1,
                                source='hive',
                                badges=[],
                                usage=1330,
                                parent='dynamo://gold.test_schema/test_table2')
                ],
                downstream_entities=[
                    LineageItem(
                        key="hive://gold.test_schema/test's_table4",
                        level=1,
                        source='hive',
                        badges=[],
                        usage=0,
                        parent='dynamo://gold.test_schema/test_table2'),
                    LineageItem(key='hive://gold.test_schema/test_table3',
                                level=1,
                                source='hive',
                                badges=[],
                                usage=0,
                                parent='dynamo://gold.test_schema/test_table2')
                ])

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            actual = nebula_proxy.get_lineage(id=key, resource_type=ResourceType.Table, direction="both", depth=4)
            self.assertEqual(expected.__repr__(), actual.__repr__())

    def test_get_feature_success(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [{
                        'type': 'vertex',
                        'id': 'feature_group_1/feature meta 1/v0alpha1'
                    }, {
                        'type':
                        'vertex',
                        'id':
                        'feature_group_1/feature meta 1/v0alpha1/_description'
                    }, {
                        'type': 'vertex',
                        'id': 'feature_group_1'
                    }, [],
                             [{
                                 'type': 'vertex',
                                 'id': 'database://database://hive'
                             }, {
                                 'type': 'vertex',
                                 'id': 'database://database://dynamo'
                             }], [],
                             [{
                                 'type': 'vertex',
                                 'id': 'tag2'
                             }, {
                                 'type': 'vertex',
                                 'id': 'tag1'
                             }], [], []],
                    'row': [{
                        'Feature.data_type': 'data_type_1',
                        'Feature.published_tag': 'unique_tag',
                        'Feature.last_updated_timestamp': '1070230473',
                        'Feature.name': 'feature meta 1',
                        'Feature.publisher_last_updated_epoch_ms': 1649237249,
                        'Feature.version': 'v0alpha1',
                        'Feature.created_timestamp': '1560490521',
                        'Feature.entity': 'feature_es_key1'
                    }, {
                        'Description.published_tag': 'unique_tag',
                        'Description.publisher_last_updated_epoch_ms':
                        1649237259,
                        'Description.description_source': 'description',
                        'Description.description': 'description'
                    }, {
                        'Feature_Group.name':
                        'feature_group_1',
                        'Feature_Group.published_tag':
                        'unique_tag',
                        'Feature_Group.publisher_last_updated_epoch_ms':
                        1649237249
                    }, [],
                            [{
                                'Database.name':
                                'database://hive',
                                'Database.published_tag':
                                'unique_tag',
                                'Database.publisher_last_updated_epoch_ms':
                                1649237259
                            }, {
                                'Database.name':
                                'database://dynamo',
                                'Database.published_tag':
                                'unique_tag',
                                'Database.publisher_last_updated_epoch_ms':
                                1649237259
                            }], [],
                            [{
                                'Tag.tag_type': 'default',
                                'Tag.published_tag': 'unique_tag',
                                'Tag.publisher_last_updated_epoch_ms':
                                1649259854
                            }, {
                                'Tag.tag_type': 'default',
                                'Tag.published_tag': 'unique_tag',
                                'Tag.publisher_last_updated_epoch_ms':
                                1649259854
                            }], [], []]
                }],
                'columns': [
                    'feat', 'description', 'fg', 'wmk_records',
                    'availability_records', 'owner_records', 'tag_records',
                    'badge_records', 'prog_descriptions'
                ],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            feature = nebula_proxy.get_feature(feature_uri='dummy_uri')
            expected = Feature(
                key='feature_group_1/feature meta 1/v0alpha1',
                name='feature meta 1',
                version='v0alpha1',
                status=None,
                feature_group='feature_group_1',
                entity='feature_es_key1',
                data_type='data_type_1',
                availability=['database://hive', 'database://dynamo'],
                description='description',
                owners=[],
                badges=[],
                tags=[
                    Tag(tag_type='default', tag_name='tag2'),
                    Tag(tag_type='default', tag_name='tag1')
                ],
                programmatic_descriptions=[],
                watermarks=[],
                last_updated_timestamp=1070230473,
                created_timestamp=None)
            self.assertEqual(str(expected), str(feature))

    def test_get_feature_not_found(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [],
                'columns': [
                    'feat', 'description', 'fg', 'wmk_records',
                    'availability_records', 'owner_records', 'tag_records',
                    'badge_records', 'prog_descriptions'
                ],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')

            self.assertRaises(NotFoundException, nebula_proxy._exec_feature_query, feature_key='invalid_feat_uri')
            self.assertRaises(NotFoundException, nebula_proxy.get_feature, feature_uri='invalid_feat_uri')

    def test_get_resource_generation_code_success(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName':
                'amundsen',
                'data': [{
                    'meta': [{
                        'type':
                        'vertex',
                        'id':
                        'test_feature_group/test_feature_name/1.2.3/_generation_code'
                    }],
                    'row': [{
                        'Feature_Generation_Code.source':
                        'test_source',
                        'Feature_Generation_Code.text':
                        'SELECT * FROM test_table',
                        'Feature_Generation_Code.publisher_last_updated_epoch_ms':
                        1649237260,
                        'Feature_Generation_Code.published_tag':
                        'unique_tag',
                        'Feature_Generation_Code.last_executed_timestamp':
                        '1514604904'
                    }]
                }],
                'columns': ['query_records'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]

            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')
            gen_code = nebula_proxy.get_resource_generation_code(uri='dummy_uri',
                                                                resource_type=ResourceType.Feature)
            expected = GenerationCode(key='test_feature_group/test_feature_name/1.2.3/_generation_code',
                                      text='SELECT * FROM test_table',
                                      source='test_source')
        self.assertEqual(str(expected), str(gen_code))

    def test_get_resource_generation_code_not_found(self) -> None:
        with patch.object(NebulaProxy, 'init_connection'), patch.object(
                NebulaProxy, '_execute_query') as mock_execute:
            mock_execute.return_value = [{
                'spaceName': 'amundsen',
                'data': [],
                'columns': ['query_records'],
                'errors': {
                    'code': 0
                },
                'latencyInUs': 1
            }]
            nebula_proxy = NebulaProxy(host='DOES_NOT_MATTER',
                                       port=0000,
                                       user='u',
                                       password='psw')

            self.assertRaises(NotFoundException,
                              nebula_proxy.get_resource_generation_code,
                              uri='invalid_feat_uri',
                              resource_type=ResourceType.Feature)

class TestNebulaProxyHelpers:
    CreateAppsTestCase = namedtuple('CreateAppsTestCase',
                                    ['input_producing', 'input_consuming', 'table_writer', 'table_apps'])

    def test_create_apps(self) -> None:
        def _get_test_record(app_id: str) -> dict:
            return {'name': 'SomeApp', 'application_url': 'https://foo.bar', 'id': app_id}

        test_cases = [
            self.CreateAppsTestCase(
                input_producing=[],
                input_consuming=[],
                table_writer=None,
                table_apps=[],
            ),
            self.CreateAppsTestCase(
                input_producing=[_get_test_record('1')],
                input_consuming=[],
                table_writer=Application(**_get_test_record('1'), kind='Producing'),
                table_apps=[
                    Application(**_get_test_record('1'), kind='Producing'),
                ],
            ),
            self.CreateAppsTestCase(
                input_producing=[_get_test_record('1'), _get_test_record('2')],
                input_consuming=[_get_test_record('3')],
                table_writer=Application(**_get_test_record('1'), kind='Producing'),
                table_apps=[
                    Application(**_get_test_record('1'), kind='Producing'),
                    Application(**_get_test_record('2'), kind='Producing'),
                    Application(**_get_test_record('3'), kind='Consuming'),
                ],
            ),
            self.CreateAppsTestCase(
                input_producing=[],
                input_consuming=[_get_test_record('3')],
                table_writer=None,
                table_apps=[
                    Application(**_get_test_record('3'), kind='Consuming'),
                ],
            ),
            self.CreateAppsTestCase(
                input_producing=[_get_test_record('1')],
                input_consuming=[_get_test_record('1'), _get_test_record('2')],
                table_writer=Application(**_get_test_record('1'), kind='Producing'),
                table_apps=[
                    Application(**_get_test_record('1'), kind='Producing'),
                    Application(**_get_test_record('2'), kind='Consuming'),
                ],
            )
        ]

        with patch.object(NebulaProxy, 'init_connection'):
            proxy = NebulaProxy(host='DOES_NOT_MATTER', port=0000, user ='u', password='psw')

            for tc in test_cases:
                actual_table_writer, actual_table_apps = proxy._create_apps(tc.input_producing, tc.input_consuming)
                assert (actual_table_writer, actual_table_apps) == (tc.table_writer, tc.table_apps)

if __name__ == '__main__':
    unittest.main()
