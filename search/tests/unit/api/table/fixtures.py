from search_service.models.table import Table
from search_service.models.tag import Tag


def mock_proxy_results() -> Table:
    return Table(name='hello',
                 key='world',
                 description='des1',
                 cluster='clust',
                 database='db',
                 display_name=None,
                 schema='schema',
                 column_names=['col1', 'col2'],
                 tags=[Tag(tag_name='tag')],
                 badges=[Tag(tag_name='badge1')],
                 last_updated_timestamp=1568324871)


def mock_json_response() -> dict:
    return {
        "name": "hello",
        "key": "world",
        "description": "des1",
        "display_name": None,
        "cluster": "clust",
        "database": "db",
        "schema": "schema",
        "column_names": ["col1", "col2"],
        "tags": [{'tag_name': 'tag'}],
        "badges": [{'tag_name': 'badge1'}],
        "last_updated_timestamp": 1568324871,
    }


def default_json_response() -> dict:
    return {
        "name": None,
        "key": None,
        "description": None,
        "cluster": None,
        "database": None,
        "display_name": None,
        "schema": None,
        "column_names": None,
        "tags": None,
        "badges": None,
        "last_updated_timestamp": 0,
    }
