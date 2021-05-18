# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import copy
from typing import Dict, List


class DottedDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__  # type: ignore
    __delattr__ = dict.__delitem__  # type: ignore


class Data:
    entity_type = 'hive_table'
    column_type = 'hive_column'
    cluster = 'TEST_CLUSTER'
    db = 'TEST_DB'
    name = 'TEST_TABLE'
    table_uri = f'{entity_type}://{cluster}.{db}/{name}'

    active_columns = 4
    inactive_columns = 7

    classification_entity = {
        'classifications': [
            {'typeName': 'PII_DATA', 'name': 'PII_DATA'},
        ]
    }

    test_column = {
        'guid': 'COLUMN_GUID',
        'typeName': 'COLUMN',
        'entityStatus': 'ACTIVE',
        'attributes': {
            'name': 'column name',
            'qualifiedName': 'column@name',
            'type': 'Managed',
            'description': 'column description',
            'position': 1,
            'statistics': [
                {'attributes': {
                    'stat_name': 'max',
                    'stat_val': 100.1234,
                    'start_epoch': '100',
                    'end_epoch': '200',
                }},
                {'attributes': {
                    'stat_name': 'min',
                    'stat_val': 0.5678,
                    'start_epoch': '100',
                    'end_epoch': '200',
                }},
            ]
        },
        "classifications": [
            {
                "typeName": "active_col_badge",
                "entityStatus": "ACTIVE"
            },
            {
                "typeName": "inactive_col_badge",
                "entityStatus": "INACTIVE"
            }
        ]
    }

    test_column_inactive = copy.deepcopy(test_column)
    test_column_inactive['entityStatus'] = 'INACTIVE'

    test_exp_col_stats_raw = [
        {'attributes': {
            'stat_name': 'max',
            'stat_val': '100.1234',
            'start_epoch': '100',
            'end_epoch': '200',
        }},
        {'attributes': {
            'stat_name': 'min',
            'stat_val': '0.5678',
            'start_epoch': '100',
            'end_epoch': '200',
        }},
    ]

    test_exp_col_stats_formatted = [
        {'attributes': {
            'stat_name': 'minimum',
            'stat_val': '0.57',
            'start_epoch': '100',
            'end_epoch': '200',
        }},
    ]

    db_entity = {
        'guid': '-100',
        'updateTime': 2345678901234,
        'typeName': entity_type,
        'attributes': {
            'qualifiedName': db,
            'name': 'db',
            'description': 'Dummy DB Description',
            'owner': 'dummy@email.com',
        }
    }

    partition_entity_1 = {
        'typeName': 'table_partition',
        'status': 'INACTIVE',
        'attributes': {
            'name': '20200908'
        },
        'createTime': 1599723564000
    }

    partition_entity_2 = {
        'typeName': 'table_partition',
        'status': 'ACTIVE',
        'attributes': {
            'name': '20200909'
        },
        'createTime': 1599723564000
    }

    partition_entity_3 = {
        'typeName': 'table_partition',
        'status': 'ACTIVE',
        'attributes': {
            'name': '20200910'
        },
        'createTime': 1599723564000
    }

    partition_entity_4 = {
        'typeName': 'table_partition',
        'status': 'ACTIVE',
        'attributes': {
            'name': '2020,8'
        },
        'createTime': 1599723564000
    }

    partitions: List[Dict] = [partition_entity_1, partition_entity_2, partition_entity_3, partition_entity_4]

    entity1 = {
        'guid': '1',
        'typeName': entity_type,
        'updateTime': 1234567890123,
        'attributes': {
            'qualifiedName': '{}.{}@{}'.format(db, 'Table1', cluster),
            'name': 'Table1',
            'description': 'Dummy Description',
            'owner': 'dummy@email.com',
            'db': db_entity,
            'popularityScore': 100,
            'partitions': list(),
            'parameters': {
                'testParameterKeyB': 'testParameterValueB',
                'testParameterKeyA': 'testParameterValueA',
                'spark.sql.param': 1
            },
            'reports': [{'guid': '23'}, {'guid': '121212'}, {'guid': '2344'}],
            'tableType': 'MANAGED_TABLE'
        },
        'relationshipAttributes': {
            'db': db_entity,
            'columns': ([test_column_inactive] * inactive_columns) + ([test_column] * active_columns),
            'ownedBy': [
                {
                    "entityStatus": "ACTIVE",
                    "relationshipStatus": "ACTIVE",
                    "guid": "000",
                    "displayText": "active_owned_by"
                },
                {
                    "entityStatus": "ACTIVE",
                    "relationshipStatus": "DELETED",
                    "guid": "111",
                    "displayText": "deleted_owned_by"
                }
            ],
            'partitions': [dict(displayText=p.get('attributes', dict()).get('name'),
                                entityStatus=p.get('status'),
                                relationshipStatus='ACTIVE') for p in partitions]
        },
    }
    entity1.update(classification_entity)

    entity2 = {
        'guid': '2',
        'updateTime': 234,
        'typeName': entity_type,
        'attributes': {
            'qualifiedName': '{}.{}@{}'.format(db, 'Table2', cluster),
            'name': 'Table2',
            'description': 'Dummy Description',
            'owner': 'dummy@email.com',
            'db': db_entity,
            'popularityScore': 100,
            'partitions': list(),
            'tableType': 'VIRTUAL_VIEW'
        },
        'relationshipAttributes': {
            'db': db_entity
        },
    }
    entity2.update(classification_entity)

    entities = {
        'entities': [
            entity1,
            entity2,
        ]
    }

    bookmark_entity1 = {
        "typeName": "Bookmark",
        "attributes": {
            "active": True,
            "qualifiedName": '{}.{}.{}.{}.bookmark@{}'.format(db, name, 'hive_table', 'test_user_id', cluster),
            "entityUri": table_uri,
        },
        "guid": "0fa40fd5-016c-472e-a72f-25a5013cc818",
        "status": "ACTIVE",
        "displayText": '{}.{}.{}.{}.bookmark@{}'.format(db, name, 'hive_table', 'test_user_id', cluster),
        "classificationNames": [],
        "meaningNames": [],
        "meanings": []
    }

    bookmark_entity2 = {
        "typeName": "Bookmark",
        "attributes": {
            "active": True,
            "qualifiedName": '{}.{}.{}.{}.bookmark@{}'.format(db, 'Table2', 'hive_table', 'test_user_id', cluster),
            "entityUri": table_uri,
        },
        "guid": "0fa40fd5-016c-472e-a72f-a72ffa40fd5",
        "status": "ACTIVE",
        "displayText": '{}.{}.{}.{}.bookmark@{}'.format(db, 'Table2', 'hive_table', 'test_user_id', cluster),
        "classificationNames": [],
        "meaningNames": [],
        "meanings": []
    }

    bookmark_entities = {
        'entities': [
            bookmark_entity1,
            bookmark_entity2,
        ]
    }

    user_entity_1 = {
        "typeName": "User",
        "attributes": {
            "qualifiedName": "test_user_1"
        },
        "guid": "",
        "status": "ACTIVE",
        "displayText": 'test_user_1',
        "classificationNames": [],
        "meaningNames": [],
        "meanings": []
    }

    user_entity_2 = {
        "typeName": "User",
        "attributes": {
            "qualifiedName": "test_user_2"
        },
        "guid": "",
        "status": "ACTIVE",
        "displayText": 'test_user_2',
        "classificationNames": [],
        "meaningNames": [],
        "meanings": [],
        "relationshipAttributes": {
            "entityReads": [
                {
                    "entityStatus": "ACTIVE",
                    "relationshipStatus": "ACTIVE",
                    "guid": "1"
                },
                {
                    "entityStatus": "INACTIVE",
                    "relationshipStatus": "ACTIVE",
                    "guid": "2"
                },
                {
                    "entityStatus": "ACTIVE",
                    "relationshipStatus": "INACTIVE",
                    "guid": "3"
                }
            ],
            "owns": [
                {
                    "entityStatus": "ACTIVE",
                    "relationshipStatus": "ACTIVE",
                    "typeName": entity_type,
                    "guid": entity1["guid"]
                },
                {
                    "entityStatus": "ACTIVE",
                    "relationshipStatus": "DELETED",
                    "typeName": entity_type,
                    "guid": entity2["guid"]
                }]
        }
    }

    reader_entity_1 = {
        "typeName": "Reader",
        "attributes": {
            "count": 5,
            "qualifiedName": '{}.{}.{}.reader@{}'.format(db, 'Table1', 'test_user_1', cluster),
            "entityUri": f"hive_table://{cluster}.{db}/Table1",
        },
        "guid": "1",
        "status": "ACTIVE",
        "displayText": '{}.{}.{}.reader@{}'.format(db, 'Table1', 'test_user', cluster),
        "classificationNames": [],
        "meaningNames": [],
        "meanings": [],
        "relationshipAttributes": {"user": user_entity_1}
    }

    reader_entity_2 = {
        "typeName": "Reader",
        "attributes": {
            "count": 150,
            "qualifiedName": '{}.{}.{}.reader@{}'.format(db, 'Table1', 'test_user_2', cluster),
            "entityUri": f"hive_table://{cluster}.{db}/Table1",
        },
        "guid": "2",
        "status": "ACTIVE",
        "displayText": '{}.{}.{}.reader@{}'.format(db, 'Table1', 'test_user_2', cluster),
        "classificationNames": [],
        "meaningNames": [],
        "meanings": [],
        "relationshipAttributes": {"user": user_entity_2}
    }

    reader_entities = [DottedDict(reader_entity) for reader_entity in [reader_entity_1, reader_entity_2]]

    report_entity_1 = {
        'typeName': 'Report',
        'status': 'ACTIVE',
        'attributes': {
            'name': "test_report",
            'url': "http://test"
        }}
    report_entity_2 = {
        'typeName': 'Report',
        'status': 'DELETED',
        'attributes': {
            'name': "test_report2",
            'url': "http://test2"
        }}
    report_entity_3 = {
        'typeName': 'Report',
        'status': 'ACTIVE',
        'attributes': {
            'name': "test_report3",
            'url': "http://test3"
        }}

    report_entities = [report_entity_1, report_entity_2, report_entity_3]

    metrics_data = DottedDict({
        'general': {
            'stats': {
                'Notification:lastMessageProcessedTime': 1598342400000
            }
        }
    })

    dashboard_data = DottedDict({
        'referredEntities': {
            'query_1': {
                'typeName': 'DashboardQuery',
                'attributes': {
                    'qualifiedName': 'superset_dashboard://datalab.prod/1/query/1',
                    'url': 'https://prod.superset/dashboards/1/query/1',
                    'name': 'User Count By Time',
                    'queryText': 'SELECT date, COUNT(1) FROM db.table GROUP BY 1',
                    'id': 'user_count_by_time',
                    'chart': {
                        'guid': 'beb07782-e6ed-4e18-abcf-669d69152cf1',
                        'typeName': 'DashboardChart'
                    }
                },
                'guid': 'query_1',
                'status': 'ACTIVE'
            },
            'execution_1': {
                'typeName': 'DashboardExecution',
                'attributes': {
                    'qualifiedName': 'superset_dashboard://datalab.prod/1/execution/1',
                    'state': 'succeeded',
                    'timestamp': 1619517099
                },
                'guid': 'execution_1',
                'status': 'ACTIVE',
                'createTime': 1620327423719,
                'updateTime': 1620327423719
            },
            'execution_2': {
                'typeName': 'DashboardExecution',
                'attributes': {
                    'qualifiedName': 'superset_dashboard://datalab.prod/1/execution/2',
                    'state': 'failed',
                    'timestamp': 1619517150
                },
                'guid': 'execution_2',
                'status': 'ACTIVE',
                'createTime': 1620327423720,
                'updateTime': 1620327423730
            },
            'query_2': {
                'typeName': 'DashboardQuery',
                'attributes': {
                    'qualifiedName': 'superset_dashboard://datalab.prod/1/query/2',
                    'url': 'https://prod.superset/dashboards/1/query/2',
                    'name': 'Total Count',
                    'queryText': 'SELECT COUNT(1) FROM db.table',
                    'id': 'total_count'
                },
                'guid': 'query_2',
                'status': 'ACTIVE',
                'createTime': 1620327423719,
                'updateTime': 1620327423719
            },
            'chart_2': {
                'typeName': 'DashboardChart',
                'attributes': {
                    'qualifiedName': 'superset_dashboard://datalab.prod/1/query/2/chart/1',
                    'type': 'horizontal_bar',
                    'url': 'https://prod.superset/dashboards/1/chart/2',
                    'name': 'Count Users by Time'
                },
                'guid': 'chart_2',
                'status': 'ACTIVE',
                'createTime': 1620327423719,
                'updateTime': 1620327423719
            },
            'chart_1': {
                'typeName': 'DashboardChart',
                'attributes': {
                    'qualifiedName': 'superset_dashboard://datalab.prod/1/query/1/chart/1',
                    'type': 'metric',
                    'url': 'https://prod.superset/dashboards/1/chart/1',
                    'name': 'Total Count'
                },
                'guid': 'chart_1',
                'status': 'ACTIVE',
                'createTime': 1620327423719,
                'updateTime': 1620327423719
            }
        },
        'entity': {
            'typeName': 'Dashboard',
            'attributes': {
                'popularityScore': 0,
                'cluster': 'datalab',
                'product': 'superset',
                'charts': [
                    {
                        'guid': 'chart_2',
                        'typeName': 'DashboardChart'
                    },
                    {
                        'guid': 'chart_1',
                        'typeName': 'DashboardChart'
                    }
                ],
                'qualifiedName': 'superset_dashboard://datalab.prod/1',
                'createdTimestamp': 1619517099,
                'description': 'Robs famous dashboard',
                'url': 'https://prod.superset/dashboards/1',
                'lastModifiedTimestamp': 1619626531,
                'bookmarks': [],
                'tables': [
                    {
                        'guid': 'table_1',
                        'typeName': 'hive_table'
                    }
                ],
                'executions': [
                    {
                        'guid': 'execution_1',
                        'typeName': 'DashboardExecution'
                    },
                    {
                        'guid': 'execution_2',
                        'typeName': 'DashboardExecution'
                    }
                ],
                'readers': [],
                'name': 'Prod Usage',
                'group': {
                    'guid': 'group_1',
                    'typeName': 'DashboardGroup'
                }
            },
            'guid': 'dashboard_1',
            'relationshipAttributes': {
                'bookmarks': [],
                'reports': [],
                'tables': [
                    {
                        'guid': 'table_1',
                        'typeName': 'hive_table',
                        'entityStatus': 'ACTIVE',
                        'displayText': 'carlson_group',
                        'relationshipType': 'Table__Dashboard',
                        'relationshipGuid': 'd0443458-18df-4ab6-8704-c3535f437072',
                        'relationshipStatus': 'ACTIVE',
                        'relationshipAttributes': {
                            'typeName': 'Table__Dashboard'
                        }
                    }
                ],
                'charts': [
                    {
                        'guid': 'chart_2',
                        'typeName': 'DashboardChart',
                        'entityStatus': 'ACTIVE',
                        'displayText': 'Count Users by Time',
                        'relationshipType': 'Dashboard__DashboardChart',
                        'relationshipGuid': '2eedcf38-fa26-4806-ae95-ab7596c72ea7',
                        'relationshipStatus': 'ACTIVE',
                        'relationshipAttributes': {
                            'typeName': 'Dashboard__DashboardChart'
                        }
                    },
                    {
                        'guid': 'chart_1',
                        'typeName': 'DashboardChart',
                        'entityStatus': 'ACTIVE',
                        'displayText': 'Total Count',
                        'relationshipType': 'Dashboard__DashboardChart',
                        'relationshipGuid': '7c645759-f464-41ea-b2ce-6157add585f5',
                        'relationshipStatus': 'ACTIVE',
                        'relationshipAttributes': {
                            'typeName': 'Dashboard__DashboardChart'
                        }
                    }
                ],
                'executions': [
                    {
                        'guid': 'execution_1',
                        'typeName': 'DashboardExecution',
                        'entityStatus': 'ACTIVE',
                        'displayText': 'superset_dashboard://datalab.prod/1/execution/1',
                        'relationshipType': 'Dashboard__DashboardExecution',
                        'relationshipGuid': '56d091b8-be4d-44fe-b7c5-85e6d2649825',
                        'relationshipStatus': 'ACTIVE',
                        'relationshipAttributes': {
                            'typeName': 'Dashboard__DashboardExecution'
                        }
                    },
                    {
                        'guid': 'execution_2',
                        'typeName': 'DashboardExecution',
                        'entityStatus': 'ACTIVE',
                        'displayText': 'superset_dashboard://datalab.prod/1/execution/2',
                        'relationshipType': 'Dashboard__DashboardExecution',
                        'relationshipGuid': '56d091b8-be4d-44fe-b7c5-85e6d2649825',
                        'relationshipStatus': 'ACTIVE',
                        'relationshipAttributes': {
                            'typeName': 'Dashboard__DashboardExecution'
                        }
                    }
                ],
                'readers': [],
                'ownedBy': [
                    {
                        'guid': '547d835a-e3fa-440d-aa3e-8383215d7e3c',
                        'typeName': 'User',
                        'entityStatus': 'ACTIVE',
                        'displayText': 'lisa_salinas',
                        'relationshipType': 'Dashboard_Users_Owner',
                        'relationshipGuid': '4f67ea6d-5db4-429c-9ecd-69c751e78aed',
                        'relationshipStatus': 'ACTIVE',
                        'relationshipAttributes': {
                            'typeName': 'Dashboard_Users_Owner'
                        }
                    }
                ],
                'meanings': [],
                'group': {
                    'guid': 'group_1',
                    'typeName': 'DashboardGroup',
                    'entityStatus': 'ACTIVE',
                    'displayText': 'prod superset',
                    'relationshipType': 'DashboardGroup__Dashboard',
                    'relationshipGuid': '430291b7-e17d-4e46-8aae-0ff8c10ec675',
                    'relationshipStatus': 'ACTIVE',
                    'relationshipAttributes': {
                        'typeName': 'DashboardGroup__Dashboard'
                    }
                }
            },
            'classifications': ['transactions'],
            'meanings': [],
            'labels': [],
            'status': 'ACTIVE',
            'createTime': 1620327423719,
            'updateTime': 1620327423719
        }
    })

    dashboard_group_data = DottedDict({
        'attributes': {
            'name': 'prod superset',
            'url': 'https://superset.prod'
        }

    })
