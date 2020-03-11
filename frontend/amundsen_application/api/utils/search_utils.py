from typing import Dict, List  # noqa: F401


# These can move to a configuration when we have custom use cases outside of these default values
valid_search_fields = {
    'column',
    'database',
    'schema',
    'table',
    'tag'
}


def map_table_result(result: Dict) -> Dict:
    return {
        'type': 'table',
        'key': result.get('key', None),
        'name': result.get('name', None),
        'cluster': result.get('cluster', None),
        'description': result.get('description', None),
        'database': result.get('database', None),
        'schema': result.get('schema', None),
        'badges': result.get('badges', None),
        'last_updated_timestamp': result.get('last_updated_timestamp', None),
    }


def transform_filters(*, filters: Dict = {}) -> Dict:
    """
    Transforms the data shape of filters from the application to the data
    shape required by the search service according to the api defined at:
    https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/api/swagger_doc/table/search_table_filter.yml
    """
    filter_payload = {}
    for category in valid_search_fields:
        values = filters.get(category)
        value_list = []  # type: List
        if values is not None:
            if type(values) == str:
                value_list = [values, ]
            elif type(values) == dict:
                value_list = [key for key in values.keys() if values[key] is True]
        if len(value_list) > 0:
            filter_payload[category] = value_list

    return filter_payload


def generate_query_json(*, filters: Dict = {}, page_index: int, search_term: str) -> Dict:
    """
    Transforms the given paramaters to the query json for the search service according to
    the api defined at:
    https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/api/swagger_doc/table/search_table_filter.yml
    """
    return {
        'page_index': int(page_index),
        'search_request': {
            'type': 'AND',
            'filters': filters
        },
        'query_term': search_term
    }


def has_filters(*, filters: Dict = {}) -> bool:
    """
    Returns whether or not the filter dictionary passed to the search service
    has at least one filter value for a valid filter category
    """
    for category in valid_search_fields:
        filter_list = filters.get(category, [])
        if len(filter_list) > 0:
            return True
    return False
