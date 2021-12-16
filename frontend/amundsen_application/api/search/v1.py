# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import json

from http import HTTPStatus

from typing import Any, Dict, List  # noqa: F401

from flask import Response, jsonify, make_response, request
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_common.models.search import Filter, SearchRequestSchema, SearchResponseSchema

from amundsen_application.api.utils.request_utils import get_query_param, request_search
from amundsen_application.api.utils.search_utils import generate_query_request, map_dashboard_result, map_feature_result, map_table_result, map_user_result

LOGGER = logging.getLogger(__name__)

REQUEST_SESSION_TIMEOUT_SEC = 3

SEARCH_ENDPOINT = '/v2/search'

RESOURCE_TO_MAPPING = {
    'table': map_table_result,
    'dashboard':  map_dashboard_result,
    'feature': map_feature_result,
    'user': map_user_result,
}

search_blueprint = Blueprint('search', __name__, url_prefix='/api/search/v1')

def _transform_filters(filters: Dict) -> List[Filter]:
    transformed_filters = []
    for resource in filters.keys():
        resource_filters = filters[resource]
        for field in resource_filters.keys():
            values = []
            if type(resource_filters[field]) == dict:
                values = list(resource_filters[field].keys())
            else:
                values = [resource_filters[field]]
            transformed_filters.append(Filter(name=field,
                                              values=values,
                                              operation='OR'))

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
        results_per_page = get_query_param(request_json, 'resultsPerPage', '"resultsPerPage" parameter expected in request data')
        resources = get_query_param(request_json, 'resources')
        search_type = request_json.get('searchType')
        transformed_filters = _transform_filters(filters=request_json.get('filters', {}))
        results_dict = _search_resources(search_term=search_term,
                                         resources=resources,
                                         page_index=page_index,
                                         results_per_page=results_per_page,
                                         filters=transformed_filters,
                                         search_type=search_type)
        return make_response(jsonify(results_dict), results_dict.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR))
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        LOGGER.exception(message)
        return make_response(jsonify(results_dict), HTTPStatus.INTERNAL_SERVER_ERROR)


def _search_resources(*, search_term: str,
                      resources: List[str],
                      page_index: int,
                      results_per_page: int,
                      filters: List[Filter],
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
        query_request = generate_query_request(filters=filters,
                                            resources=resources,
                                            page_index=page_index,
                                            results_per_page=results_per_page,
                                            search_term=search_term)
        request_json = json.dumps(SearchRequestSchema().dump(query_request))
        url_base = app.config['SEARCHSERVICE_BASE'] + SEARCH_ENDPOINT
        response = request_search(url=url_base,
                                    headers={'Content-Type': 'application/json'},
                                    method='POST',
                                    data=request_json)
        search_response = SearchResponseSchema().loads(json.dumps(response.json()))                            
        LOGGER.info(search_response)
        status_code = search_response.status_code

        if status_code == HTTPStatus.OK:
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
