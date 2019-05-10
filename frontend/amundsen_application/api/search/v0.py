import logging

from http import HTTPStatus

from typing import Any, Dict, Optional

from flask import Response, jsonify, make_response, request
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_application.log.action_log import action_logging
from amundsen_application.api.utils.request_utils import get_query_param, request_search

LOGGER = logging.getLogger(__name__)

REQUEST_SESSION_TIMEOUT_SEC = 3

search_blueprint = Blueprint('search', __name__, url_prefix='/api/search/v0')

valid_search_fields = {
    'tag',
    'schema',
    'table',
    'column'
}

SEARCH_ENDPOINT = '/search'


def _create_error_response(*, message: str, payload: Dict, status_code: int) -> Response:
    logging.info(message)
    payload['msg'] = message
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


@search_blueprint.route('/table', methods=['GET'])
def search_table() -> Response:
    search_term = get_query_param(request.args, 'query', 'Endpoint takes a "query" parameter')
    page_index = get_query_param(request.args, 'page_index', 'Endpoint takes a "page_index" parameter')

    error_response = _validate_search_term(search_term=search_term, page_index=int(page_index))
    if error_response is not None:
        return error_response

    results_dict = _search_table(search_term=search_term, page_index=page_index)
    return make_response(jsonify(results_dict), results_dict.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR))


@search_blueprint.route('/user', methods=['GET'])
def search_user() -> Response:
    return make_response(jsonify({'msg': 'Not implemented'}), HTTPStatus.NOT_IMPLEMENTED)


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
          '?page_index={3}'.format(app.config['SEARCHSERVICE_BASE'] + SEARCH_ENDPOINT,
                                   field_key,
                                   field_val,
                                   page_index)
    if search_term:
        url += '&query_term={0}'.format(search_term)
    return url


@action_logging
def _search_user(*, search_term: str, page_index: int) -> Dict[str, Any]:
    """
        call the search service endpoint and return matching results
        :return: a json output containing search results array as 'results'

        Schema Defined Here: https://github.com/lyft/
        amundsensearchlibrary/blob/master/search_service/api/search.py

        TODO: Define an interface for envoy_client
        """

    def _map_user_result(result: Dict) -> Dict:
        return {
            'type': 'user',
            'active': result.get('active', None),
            'birthday': result.get('birthday', None),
            'department': result.get('department', None),
            'email': result.get('email', None),
            'first_name': result.get('first_name', None),
            'github_username': result.get('github_username', None),
            'id': result.get('id', None),
            'last_name': result.get('last_name', None),
            'manager_email': result.get('manager_email', None),
            'name': result.get('name', None),
            'offboarded': result.get('offboarded', None),
            'office': result.get('office', None),
            'role': result.get('role', None),
            'start_date': result.get('start_date', None),
            'team_name': result.get('team_name', None),
            'title': result.get('title', None),
        }

    users = {
        'page_index': int(page_index),
        'results': [],
        'total_results': 0,
    }

    results_dict = {
        'search_term': search_term,
        'msg': 'Success',
        'status_code': HTTPStatus.OK,
        'users': users,
    }

    return results_dict


@action_logging
def _search_table(*, search_term: str, page_index: int) -> Dict[str, Any]:
    """
    call the search service endpoint and return matching results
    :return: a json output containing search results array as 'results'

    Schema Defined Here: https://github.com/lyft/
    amundsensearchlibrary/blob/master/search_service/api/search.py

    TODO: Define an interface for envoy_client
    """
    def _map_table_result(result: Dict) -> Dict:
        return {
            'type': 'table',
            'key': result.get('key', None),
            'name': result.get('name', None),
            'cluster': result.get('cluster', None),
            'description': result.get('description', None),
            'database': result.get('database', None),
            'schema_name': result.get('schema_name', None),
            'last_updated_epoch': result.get('last_updated_epoch', None),
        }

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
        if ':' in search_term:
            url = _create_url_with_field(search_term=search_term,
                                         page_index=page_index)
        else:
            url = '{0}?query_term={1}&page_index={2}'.format(app.config['SEARCHSERVICE_BASE'] + SEARCH_ENDPOINT,
                                                             search_term,
                                                             page_index)

        response = request_search(url=url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            results_dict['msg'] = 'Success'
            results = response.json().get('results')
            tables['results'] = [_map_table_result(result) for result in results]
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


# TODO - Implement
def _search_dashboard(*, search_term: str, page_index: int) -> Dict[str, Any]:
    return {}
