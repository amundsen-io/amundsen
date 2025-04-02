# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from http import HTTPStatus
from typing import Any, Dict, List  # noqa: F401

from amundsen_common.models.search import (Filter, SearchRequestSchema,
                                           SearchResponseSchema)
from flask import Response
from flask import current_app as app
from flask import jsonify, make_response, request
from flask.blueprints import Blueprint

from amundsen_application.log.action_log import action_logging
from amundsen_application.api.utils.request_utils import (get_query_param,
                                                          request_search)
from amundsen_application.api.utils.search_utils import (
    generate_query_request, map_dashboard_result, map_feature_result,
    map_table_result, map_user_result)

LOGGER = logging.getLogger(__name__)

REQUEST_SESSION_TIMEOUT_SEC = 3

SEARCH_ENDPOINT = '/v2/search'

RESOURCE_TO_MAPPING = {
    'table': map_table_result,
    'dashboard': map_dashboard_result,
    'feature': map_feature_result,
    'user': map_user_result,
}

DEFAULT_FILTER_OPERATION = 'OR'

search_blueprint = Blueprint('search', __name__, url_prefix='/api/search/v1')


def _transform_filters(filters: Dict, resources: List[str]) -> List[Filter]:
    transformed_filters = []
    searched_resources_with_filters = set(filters.keys()).intersection(resources)
    for resource in searched_resources_with_filters:
        resource_filters = filters[resource]
        for field in resource_filters.keys():
            field_filters = resource_filters[field]
            values = []
            filter_operation = DEFAULT_FILTER_OPERATION

            if field_filters is not None and field_filters.get('value') is not None:
                value_str = field_filters.get('value')
                values = [str.strip() for str in value_str.split(',') if str != '']
                filter_operation = field_filters.get('filterOperation', DEFAULT_FILTER_OPERATION)

            transformed_filters.append(Filter(name=field,
                                              values=values,
                                              operation=filter_operation))

    return transformed_filters


@search_blueprint.route('/search', methods=['POST'])
def search() -> Response:
    """
    Parse the request arguments and call the helper method to execute a search for specified resources
    :return: a Response created with the results from the helper method
    """
    results_dict = {}
    try:
        request_json = request.get_json()
        search_term = get_query_param(request_json, 'searchTerm', '"searchTerm" parameter expected in request data')
        page_index = get_query_param(request_json, 'pageIndex', '"pageIndex" parameter expected in request data')
        results_per_page = get_query_param(request_json,
                                           'resultsPerPage',
                                           '"resultsPerPage" parameter expected in request data')
        search_type = request_json.get('searchType')
        resources = request_json.get('resources', [])
        filters = request_json.get('filters', {})
        highlight_options = request_json.get('highlightingOptions', {})
        results_dict = _search_resources(search_term=search_term,
                                         resources=resources,
                                         page_index=int(page_index),
                                         results_per_page=int(results_per_page),
                                         filters=filters,
                                         highlight_options=highlight_options,
                                         search_type=search_type)
        return make_response(jsonify(results_dict), results_dict.get('status_code', HTTPStatus.OK))
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        LOGGER.exception(message)
        return make_response(jsonify(results_dict), HTTPStatus.INTERNAL_SERVER_ERROR)


@action_logging
def _search_resources(*, search_term: str,
                      resources: List[str],
                      page_index: int,
                      results_per_page: int,
                      filters: Dict,
                      highlight_options: Dict,
                      search_type: str) -> Dict[str, Any]:
    """
    Call the search service endpoint and return matching results
    :return: a json output containing search results array as 'results'
    """
    default_results = {
        'page_index': int(page_index),
        'results': [],
        'total_results': 0,
    }

    results_dict = {
        'search_term': search_term,
        'msg': '',
        'table': default_results,
        'dashboard': default_results,
        'feature': default_results,
        'user': default_results,
    }

    try:
        transformed_filters = _transform_filters(filters=filters, resources=resources)
        query_request = generate_query_request(filters=transformed_filters,
                                               resources=resources,
                                               page_index=page_index,
                                               results_per_page=results_per_page,
                                               search_term=search_term,
                                               highlight_options=highlight_options)
        request_json = json.dumps(SearchRequestSchema().dump(query_request))
        url_base = app.config['SEARCHSERVICE_BASE'] + SEARCH_ENDPOINT
        response = request_search(url=url_base,
                                  headers={'Content-Type': 'application/json'},
                                  method='POST',
                                  data=request_json)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            search_response = SearchResponseSchema().loads(json.dumps(response.json()))
            results_dict['msg'] = search_response.msg
            results = search_response.results
            for resource in results.keys():
                results_dict[resource] = {
                    'page_index': int(page_index),
                    'results': [RESOURCE_TO_MAPPING[resource](result) for result in results[resource]['results']],
                    'total_results': results[resource]['total_results'],
                }
        else:
            message = 'Encountered error: Search request failed'
            results_dict['msg'] = message

        results_dict['status_code'] = status_code
        return results_dict

    except Exception as e:
        message = f'Encountered exception: {str(e)}'
        results_dict['msg'] = message
        LOGGER.exception(message)
        return results_dict
