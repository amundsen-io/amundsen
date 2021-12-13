# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import json

from typing import Dict, List  # noqa: F401

from http import HTTPStatus

from flask import current_app as app

from amundsen_common.models.search import UpdateDocumentRequestSchema, UpdateDocumentRequest

from amundsen_application.api.utils.request_utils import request_search


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


def map_table_result(result: Dict) -> Dict:
    return {
        'type': 'table',
        'key': result.get('key', None),
        'name': result.get('name', None),
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


def transform_filters(*, filters: Dict = {}, resource: str) -> Dict:
    """
    Transforms the data shape of filters from the application to the data
    shape required by the search service according to the api defined at:
    https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/api/swagger_doc/table/search_table_filter.yml
    https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/api/swagger_doc/dashboard/search_dashboard_filter.yml
    """
    LOGGER.info(filters)
    filter_payload = {}
    for category in valid_search_fields.get(resource, {}):
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


def update_search_field(key: str, resource_type: str, field: str, value: str, operation: str, method: str):
    if method not in ['POST', 'DELETE']:
        return HTTPStatus.BAD_REQUEST
    searchservice_base = app.config['SEARCHSERVICE_BASE']
    update_url = f'{searchservice_base}/v2/document'

    update_request = UpdateDocumentRequest(resource_key=key,
                                           resource_type=resource_type,
                                           field=field,
                                           value=value,
                                           operation=operation)

    request_json = json.dumps(UpdateDocumentRequestSchema().dump(update_request))
    update_response = request_search(
        url=update_url,
        method=method,
        headers={'Content-Type': 'application/json'},
        data=request_json,
    )
    if update_response.status_code != HTTPStatus.OK:
        LOGGER.info(f'Failed to update {field} in searchservice, status code: {update_response.status_code}')
        LOGGER.info(update_response.text)
        return update_response.status_code

    return HTTPStatus.OK
