# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import json

from http import HTTPStatus

from typing import Any, Dict, List  # noqa: F401

from flask import Response, jsonify, make_response, request
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_common.models.search import Filter, SearchRequest

from amundsen_application.log.action_log import action_logging
from amundsen_application.api.utils.request_utils import get_query_param, request_search
from amundsen_application.api.utils.search_utils import generate_query_request, map_table_result

LOGGER = logging.getLogger(__name__)

REQUEST_SESSION_TIMEOUT_SEC = 3

search_blueprint = Blueprint('search', __name__, url_prefix='/api/search/v1')

SEARCH_ENDPOINT = '/v2/search'

def _transform_filters(filters: Dict) -> List[Filter]:
    transformed_filters = []
    for resource in filters.keys():
        resource_filters = filters[resource]
        for field in resource_filters.keys():
            values = []
            if type(resource_filters[field]) == dict:
                values = list(values.keys())
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
        results_dict = _search_resources(filters=transformed_filters,
                                         resources=resources,
                                         search_term=search_term,
                                         page_index=page_index,
                                         results_per_page=results_per_page,
                                         search_type=search_type)
        return make_response(jsonify(results_dict), results_dict.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR))
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        LOGGER.exception(message)
        return make_response(jsonify(results_dict), HTTPStatus.INTERNAL_SERVER_ERROR)


@action_logging
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
    # Default results
    tables = {
        'page_index': int(page_index),
        'results': [],
        'total_results': 0,
    }

    results_dict = {
        'search_term': search_term,
        'msg': '',
        'tables': tables,
    }

    try:
        query_json = generate_query_request(filters=filters,
                                            resources=resources,
                                            page_index=page_index,
                                            results_per_page=results_per_page,
                                            search_term=search_term)
        url_base = app.config['SEARCHSERVICE_BASE'] + SEARCH_ENDPOINT
        response = request_search(url=url_base,
                                    headers={'Content-Type': 'application/json'},
                                    method='POST',
                                    data=json.dumps(query_json))
        status_code = response.status_code
        if status_code == HTTPStatus.OK:
            results_dict['msg'] = 'Success'
            results = response.json().get('results')
            tables['results'] = [map_table_result(result) for result in results]
            tables['total_results'] = response.json().get('total_results')
        else:
            message = 'Encountered error: Search request failed'
            results_dict['msg'] = message
            logging.error(message)

        results_dict['status_code'] = status_code
        return results_dict
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        results_dict['msg'] = message
        logging.exception(message)
        return results_dict
