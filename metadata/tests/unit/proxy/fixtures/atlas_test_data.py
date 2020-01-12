class Data:
    table_metadata = 'table_metadata'
    column_metadata = 'column_metadata'
    entity_type = 'hive_table'
    cluster = 'TEST_CLUSTER'
    db = 'TEST_DB'
    name = 'TEST_TABLE'
    table_uri = f'{entity_type}://{cluster}.{db}/{name}'

    classification_entity = {
        'classifications': [
            {'typeName': 'PII_DATA', 'name': 'PII_DATA'},
        ]
    }

    column_metadata_entity = {
        'guid': 'COLUMN_METADATA_GUID',
        'typeName': column_metadata,
        'updateTime': 12312312,
        'attributes': {
            'qualifiedName': 'Column_Metadata_Qualified',
            'statistics': [
                {'attributes': {
                    'stat_name': 'max',
                    'stat_val': '100',
                    'start_epoch': '100',
                    'end_epoch': '200',
                }},
                {'attributes': {
                    'stat_name': 'min',
                    'stat_val': '0',
                    'start_epoch': '100',
                    'end_epoch': '200',
                }},
            ]
        },
        'relationshipAttributes': {}
    }

    test_column = {
        'guid': 'COLUMN_GUID',
        'typeName': 'COLUMN',
        'attributes': {
            'name': 'column name',
            'qualifiedName': 'column@name',
            'type': 'Managed',
            'description': 'column description',
            'position': 1
        },
        'relationshipAttributes': {
            'metadata': column_metadata_entity
        },

    }
    column_metadata_entity['relationshipAttributes']['column'] = test_column    # type: ignore

    db_entity = {
        'guid': '-100',
        'updateTime': 234,
        'typeName': entity_type,
        'attributes': {
            'qualifiedName': db,
            'name': 'db',
            'description': 'Dummy DB Description',
            'owner': 'dummy@email.com',
        }
    }

    metadata1 = {
        'guid': '-1',
        'typeName': table_metadata,
        'updateTime': 12312312,
        'attributes': {
            'qualifiedName': 'Metadata1_Qualified',
            'popularityScore': 100
        },
        'relationshipAttributes': {}
    }

    entity1 = {
        'guid': '1',
        'typeName': entity_type,
        'updateTime': 123,
        'attributes': {
            'qualifiedName': '{}.{}@{}'.format(db, 'Table1', cluster),
            'name': 'Table1',
            'description': 'Dummy Description',
            'owner': 'dummy@email.com',
            'columns': [test_column],
            'db': db_entity
        },
        'relationshipAttributes': {
            'db': db_entity,
            'columns': [test_column],
            'metadata': metadata1
        },
    }
    entity1.update(classification_entity)
    metadata1['relationshipAttributes']['table'] = entity1    # type: ignore

    metadata2 = {
        'guid': '-2',
        'typeName': table_metadata,
        'updateTime': 12312,
        'attributes': {
            'qualifiedName': 'Metadata2_Qualified',
            'popularityScore': 200
        },
        'relationshipAttributes': {}
    }

    entity2 = {
        'guid': '2',
        'updateTime': 234,
        'typeName': entity_type,
        'attributes': {
            'qualifiedName': '{}.{}@{}'.format(db, 'Table2', cluster),
            'name': 'Table2',
            'description': 'Dummy Description',
            'owner': 'dummy@email.com',
            'db': db_entity
        },
        'relationshipAttributes': {
            'db': db_entity,
            'metadata': metadata2
        },
    }
    entity2.update(classification_entity)
    metadata2['relationshipAttributes']['table'] = entity2    # type: ignore

    entities = {
        'entities': [
            entity1,
            entity2,
        ]
    }
    reader_entity1 = {
        "typeName": "Reader",
        "attributes": {
            "isFollowing": True,
            "qualifiedName": '{}.{}.metadata.{}.reader@{}'.format(db, name, 'test_user_id', cluster),
            "count": 96,
            "entityUri": table_uri,
        },
        "guid": "0fa40fd5-016c-472e-a72f-25a5013cc818",
        "status": "ACTIVE",
        "displayText": '{}.{}.metadata.{}.reader@{}'.format(db, name, 'test_user_id', cluster),
        "classificationNames": [],
        "meaningNames": [],
        "meanings": []
    }

    reader_entity2 = {
        "typeName": "Reader",
        "attributes": {
            "isFollowing": True,
            "qualifiedName": '{}.{}.metadata.{}.reader@{}'.format(db, 'Table2', 'test_user_id', cluster),
            "count": 96
        },
        "guid": "0fa40fd5-016c-472e-a72f-a72ffa40fd5",
        "status": "ACTIVE",
        "displayText": '{}.{}.metadata.{}.reader@{}'.format(db, 'Table2', 'test_user_id', cluster),
        "classificationNames": [],
        "meaningNames": [],
        "meanings": []
    }

    reader_entities = {
        'entities': [
            reader_entity1,
            reader_entity2,
        ]
    }
