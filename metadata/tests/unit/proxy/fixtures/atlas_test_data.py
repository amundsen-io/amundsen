# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import copy


class DottedDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


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
            'columns': ([test_column_inactive] * inactive_columns) + ([test_column] * active_columns)
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
            """
                        if (item['entityStatus'] == Status.ACTIVE and
                    item['relationshipStatus'] == Status.ACTIVE and
                    item['typeName'] == resource_type):
            """
            "ownerOf": [{
                "entityStatus": "ACTIVE",
                "relationshipStatus": "ACTIVE",
                "typeName": "Table",
                "guid": entity1["guid"]
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

    metrics_data = [DottedDict({
        'general': {
            'stats': {
                'Notification:lastMessageProcessedTime': 1598342400000
            }
        }
    })]
