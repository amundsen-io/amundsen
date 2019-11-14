from search_service.models.table import Table


def mock_proxy_results():
    return Table(name='hello',
                 key='world',
                 description='des1',
                 cluster='clust',
                 database='db',
                 display_name=None,
                 schema_name='schema',
                 column_names=['col1', 'col2'],
                 tags=['tag'],
                 last_updated_epoch=1568324871)


def mock_json_response():
    return {
        "name": "hello",
        "key": "world",
        "description": "des1",
        "display_name": None,
        "cluster": "clust",
        "database": "db",
        "schema_name": "schema",
        "column_names": ["col1", "col2"],
        "tags": ['tag'],
        "last_updated_epoch": 1568324871,
    }


def default_json_response():
    return {
        "name": None,
        "key": None,
        "description": None,
        "cluster": None,
        "database": None,
        "display_name": None,
        "schema_name": None,
        "column_names": None,
        "tags": None,
        "last_updated_epoch": 0,
    }
