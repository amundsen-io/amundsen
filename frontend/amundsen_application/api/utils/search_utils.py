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
        'last_updated_timestamp': result.get('last_updated_timestamp', None),
    }


def generate_query_json(*, filters: Dict = {}, page_index: int, search_term: str) -> Dict:
    """
    Transforms the given paramaters to the query json for the search service according to
    the api defined at:
    https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/api/swagger_doc/table/search_table_filter.yml
    """
    # Generate the filter payload
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

    # Return the full query json
    return {
        'page_index': int(page_index),
        'search_request': {
            'type': 'AND',
            'filters': filter_payload
        },
        'query_term': search_term
    }


def has_filters(*, filters: Dict = {}) -> bool:
    for category in valid_search_fields:
        if filters.get(category) is not None:
            return True
    return False
