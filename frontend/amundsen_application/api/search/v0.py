import logging
import requests

from http import HTTPStatus

from typing import Any, Dict, Optional

from flask import Response, jsonify, make_response, request
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_application.log.action_log import action_logging
from amundsen_application.api.utils.request_utils import get_query_param

LOGGER = logging.getLogger(__name__)

REQUEST_SESSION_TIMEOUT = 10

search_blueprint = Blueprint('search', __name__, url_prefix='/api')

valid_search_fields = {
    'tag',
    'schema',
    'table',
    'column'
}


def _create_error_response(*, message: str, payload: Dict, status_code: int) -> Response:
    logging.info(message)
    payload['mg'] = message
    return make_response(jsonify(payload), status_code)


def _validate_search_term(*, search_term: str, page_index: int) -> Optional[Response]:
    # TODO: If we place these checks in the Reduc layer when actions are created/dispatched,
    # we can avoid checking both here and in the search components. Ticket will be filed.
    error_payload = {
        'results': [],
        'search_term': search_term,
        'total_results': 0,
        'page_index': page_index,
    }
    # use colon means user would like to search on specific fields
    if search_term.count(':') > 1:
        message = 'Encountered error: Search field should not be more than 1'
        return _create_error_response(message=message, payload=error_payload, status_code=HTTPStatus.BAD_REQUEST)
    if search_term.count(':') == 1:
        field_key = search_term.split(' ')[0].split(':')[0]
        if field_key not in valid_search_fields:
            message = 'Encountered error: Search field is invalid'
            return _create_error_response(message=message, payload=error_payload, status_code=HTTPStatus.BAD_REQUEST)
    return None


@search_blueprint.route('/search', methods=['GET'])
def search() -> Response:
    search_term = get_query_param(request.args, 'query', 'Endpoint takes a "query" parameter')
    page_index = get_query_param(request.args, 'page_index', 'Endpoint takes a "page_index" parameter')

    error_response = _validate_search_term(search_term=search_term, page_index=int(page_index))
    if error_response is not None:
        return error_response

    results_dict = _search(search_term=search_term, page_index=page_index)
    return make_response(jsonify(results_dict), results_dict.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR))


def _create_url_with_field(*, search_term: str, page_index: int) -> str:
    """
    Construct a url by searching specific field.
    E.g if we use search tag:hive test_table, search service will first
    filter all the results that
    don't have tag hive; then it uses test_table as query term to search /
    rank all the documents.

    We currently allow max 1 field.
    todo: allow search multiple fields(e.g tag:hive & schema:default test_table)

    :param search_term:
    :param page_index:
    :return:
    """
    # example search_term: tag:tag_name search_term search_term2
    fields = search_term.split(' ')
    search_field = fields[0].split(':')
    field_key = search_field[0]
    # dedup tag to all lower case
    field_val = search_field[1].lower()
    search_term = ' '.join(fields[1:])
    url = '{0}/field/{1}/field_val/{2}' \
          '?page_index={3}'.format(app.config['SEARCHSERVICE_ENDPOINT'],
                                   field_key,
                                   field_val,
                                   page_index)
    if search_term:
        url += '&query_term={0}'.format(search_term)
    return url


@action_logging
def _search(*, search_term: str, page_index: int) -> Dict[str, Any]:
    """
    call the search service endpoint and return matching results
    :return: a json output containing search results array as 'results'

    Schema Defined Here: https://github.com/lyft/
    amundsensearchlibrary/blob/master/search_service/api/search.py

    TODO: Define an interface for envoy_client
    """
    results_dict = {
        'results': [],
        'search_term': search_term,
        'total_results': 0,
        'page_index': int(page_index),
        'msg': '',
    }

    try:
        if ':' in search_term:
            url = _create_url_with_field(search_term=search_term,
                                         page_index=page_index)
        else:
            url = '{0}?query_term={1}&page_index={2}'.format(app.config['SEARCHSERVICE_ENDPOINT'],
                                                             search_term,
                                                             page_index)

        # TODO: Create an abstraction for this logic that is reused many times
        if app.config['SEARCHSERVICE_REQUEST_CLIENT'] is not None:
            envoy_client = app.config['SEARCHSERVICE_REQUEST_CLIENT']
            envoy_headers = app.config['SEARCHSERVICE_REQUEST_HEADERS']
            response = envoy_client.get(url, headers=envoy_headers, raw_response=True)
        else:
            with requests.Session() as s:
                response = s.get(url, timeout=REQUEST_SESSION_TIMEOUT)

        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            results_dict['msg'] = 'Success'
            results_dict['total_results'] = response.json().get('total_results')

            # Filter and parse the response dictionary from the search service
            params = [
                'key',
                'name',
                'cluster',
                'description',
                'database',
                'schema_name',
                'last_updated',
            ]
            results = response.json().get('results')
            results_dict['results'] = [{key: result.get(key, None) for key in params} for result in results]
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
