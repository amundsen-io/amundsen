# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import json

from http import HTTPStatus

from typing import Any, Dict  # noqa: F401

from flask import Response, jsonify, make_response, request
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_application.log.action_log import action_logging
from amundsen_application.api.utils.request_utils import get_query_param, request_search
from amundsen_application.api.utils.search_utils import generate_query_request, has_filters, \
    map_feature_result, map_table_result, transform_filters

LOGGER = logging.getLogger(__name__)

REQUEST_SESSION_TIMEOUT_SEC = 3

search_blueprint = Blueprint('search', __name__, url_prefix='/api/search/v1')

SEARCH_ENDPOINT = '/v2/search'

@search_blueprint.route('/search', methods=['POST'])
def search() -> Response:
    """
    Parse the request arguments and call the helper method to execute a search for specified resources
    :return: a Response created with the results from the helper method
    """
    results_dict = {}
    try:
        request_json = request.get_json()
        print(request_json)
        search_term = get_query_param(request_json, 'term', '"term" parameter expected in request data')
        page_index = get_query_param(request_json, 'pageIndex', '"pageIndex" parameter expected in request data')

        search_type = request_json.get('searchType')
        filts = request_json.get('filters', {})
        transformed_filters = transform_filters(filters=filts, resource='table')

        results_dict = _search_resources(filters=transformed_filters,
                                     search_term=search_term,
                                     page_index=page_index,
                                     search_type=search_type)
        return make_response(jsonify(results_dict), results_dict.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR))
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        return make_response(jsonify(results_dict), HTTPStatus.INTERNAL_SERVER_ERROR)


@action_logging
def _search_resources(*, search_term: str, page_index: int, filters: Dict, search_type: str) -> Dict[str, Any]:
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
                                            page_index=page_index,
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
