import copy


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
            'partitions': list()
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
            'partitions': list()
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
