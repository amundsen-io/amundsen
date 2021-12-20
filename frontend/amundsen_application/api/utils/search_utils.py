# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict, List  # noqa: F401
from amundsen_common.models.search import SearchRequest, Filter
from amundsen_application.models.user import load_user, dump_user
LOGGER = logging.getLogger(__name__)

# These can move to a configuration when we have custom use cases outside of these default values
valid_search_fields = {
    'table': {
        'badges',
        'column',
        'database',
        'schema',
        'table',
        'tag'
    },
    'dashboard': {
        'group_name',
        'name',
        'product',
        'tag'
    },
    'feature': {
        'badges',
        'entity',
        'feature_name',
        'feature_group',
        'tags'
    }
}

def map_dashboard_result(result: Dict) -> Dict:
    return {
        'type': 'dashboard',
        'key': result.get('key', None),
        'group_name': result.get('group_name', None),
        'name': result.get('name', None),
        'product': result.get('product', None),
        'tag': result.get('tag', None),
    }

def map_table_result(result: Dict) -> Dict:
    name = result.get('name') if result.get('name') else result.get('table')
    return {
        'type': 'table',
        'key': result.get('key', None),
        'name': name,
        'cluster': result.get('cluster', None),
        'description': result.get('description', None),
        'database': result.get('database', None),
        'schema': result.get('schema', None),
        'schema_description': result.get('schema_description', None),
        'badges': result.get('badges', None),
        'last_updated_timestamp': result.get('last_updated_timestamp', None),
    }


def map_feature_result(result: Dict) -> Dict:
    return {
        'type': 'feature',
        'description': result.get('description', None),
        'key': result.get('key', None),
        'last_updated_timestamp': result.get('last_updated_timestamp', None),
        'name': result.get('feature_name', None),
        'feature_group': result.get('feature_group', None),
        'version': result.get('version', None),
        'availability': result.get('availability', None),
        'entity': result.get('entity', None),
        'badges': result.get('badges', None),
        'status': result.get('status', None),
    }

def map_user_result(result: Dict) -> Dict:
    user_result = dump_user(load_user(result))
    user_result['type'] = 'user'
    return user_result

def generate_query_json(*, filters: Dict = {}, page_index: int, search_term: str) -> Dict:
    """
    Transforms the given paramaters to the query json for the search service according to
    the api defined at:
    https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/api/swagger_doc/table/search_table_filter.yml
    https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/api/swagger_doc/dashboard/search_dashboard_filter.yml
    """
    
    return {
        'page_index': int(page_index),
        'search_request': {
            'type': 'AND',
            'filters': filters
        },
        'query_term': search_term
    }

def generate_query_request(*, filters: List[Filter] = {},
                           resources: List[str] = [],
                           page_index: int = 0,
                           results_per_page: int = 10,
                           search_term: str) -> SearchRequest:

    return SearchRequest(query_term=search_term,
                         resource_types=resources,
                         page_index=page_index,
                         results_per_page=results_per_page,
                         filters=filters
                        )


def has_filters(*, filters: Dict = {}, resource: str = '') -> bool:
    """
    Returns whether or not the filter dictionary passed to the search service
    has at least one filter value for a valid filter category
    """
    for category in valid_search_fields.get(resource, {}):
        filter_list = filters.get(category, [])
        if len(filter_list) > 0:
            return True
    return False
