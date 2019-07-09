class Data:
    metadata_type = 'TEST_METADATA'
    entity_type = 'TEST_ENTITY'
    cluster = 'TEST_CLUSTER'
    db = 'TEST_DB'
    name = 'TEST_TABLE'
    table_uri = f'{entity_type}://{cluster}.{db}/{name}'

    classification_entity = {
        'classifications': [
            {'typeName': 'PII_DATA', 'name': 'PII_DATA'},
        ]
    }

    test_column = {
        'guid': 'DOESNT_MATTER',
        'typeName': 'COLUMN',
        'attributes': {
            'qualifiedName': 'column@name',
            'type': 'Managed',
            'description': 'column description',
            'position': 1,
            'stats': [
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
        }

    }

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
        'typeName': metadata_type,
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
    metadata1['relationshipAttributes']['parentEntity'] = entity1

    metadata2 = {
        'guid': '-2',
        'typeName': metadata_type,
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
    metadata2['relationshipAttributes']['parentEntity'] = entity2

    entities = {
        'entities': [
            entity1,
            entity2,
        ]
    }
