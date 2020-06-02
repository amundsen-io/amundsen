import logging
import json
from http import HTTPStatus
from typing import Any, Dict, Optional

from flask import Response, jsonify, make_response, request
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_application.log.action_log import action_logging

from amundsen_application.models.user import load_user, dump_user

from amundsen_application.api.utils.metadata_utils import marshall_table_partial, marshall_table_full,\
    marshall_dashboard_partial, marshall_dashboard_full
from amundsen_application.api.utils.request_utils import get_query_param, request_metadata


LOGGER = logging.getLogger(__name__)


metadata_blueprint = Blueprint('metadata', __name__, url_prefix='/api/metadata/v0')

TABLE_ENDPOINT = '/table'
LAST_INDEXED_ENDPOINT = '/latest_updated_ts'
POPULAR_TABLES_ENDPOINT = '/popular_tables/'
TAGS_ENDPOINT = '/tags/'
USER_ENDPOINT = '/user'
DASHBOARD_ENDPOINT = '/dashboard'


def _get_table_endpoint() -> str:
    table_endpoint = app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT
    if table_endpoint is None:
        raise Exception('An request endpoint for table resources must be configured')
    return table_endpoint


def _get_dashboard_endpoint() -> str:
    dashboard_endpoint = app.config['METADATASERVICE_BASE'] + DASHBOARD_ENDPOINT
    if dashboard_endpoint is None:
        raise Exception('An request endpoint for dashboard resources must be configured')
    return dashboard_endpoint


@metadata_blueprint.route('/popular_tables', methods=['GET'])
def popular_tables() -> Response:
    """
    call the metadata service endpoint to get the current popular tables
    :return: a json output containing an array of popular table metadata as 'popular_tables'

    Schema Defined Here:
    https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/api/popular_tables.py
    """
    try:
        url = app.config['METADATASERVICE_BASE'] + POPULAR_TABLES_ENDPOINT
        response = request_metadata(url=url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
            response_list = response.json().get('popular_tables')
            top4 = response_list[0:min(len(response_list), app.config['POPULAR_TABLE_COUNT'])]
            popular_tables = [marshall_table_partial(result) for result in top4]
        else:
            message = 'Encountered error: Request to metadata service failed with status code ' + str(status_code)
            logging.error(message)
            popular_tables = [{}]

        payload = jsonify({'results': popular_tables, 'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        payload = jsonify({'results': [{}], 'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/table', methods=['GET'])
def get_table_metadata() -> Response:
    """
    call the metadata service endpoint and return matching results
    :return: a json output containing a table metdata object as 'tableData'

    Schema Defined Here: https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/api/table.py
    TODO: Define type for this

    TODO: Define an interface for envoy_client
    """
    try:
        table_key = get_query_param(request.args, 'key')
        list_item_index = request.args.get('index', None)
        list_item_source = request.args.get('source', None)

        results_dict = _get_table_metadata(table_key=table_key, index=list_item_index, source=list_item_source)
        return make_response(jsonify(results_dict), results_dict.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR))
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        return make_response(jsonify({'tableData': {}, 'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)


@action_logging
def _get_table_metadata(*, table_key: str, index: int, source: str) -> Dict[str, Any]:

    results_dict = {
        'tableData': {},
        'msg': '',
    }

    try:
        table_endpoint = _get_table_endpoint()
        url = '{0}/{1}'.format(table_endpoint, table_key)
        response = request_metadata(url=url)
    except ValueError as e:
        # envoy client BadResponse is a subclass of ValueError
        message = 'Encountered exception: ' + str(e)
        results_dict['msg'] = message
        results_dict['status_code'] = getattr(e, 'code', HTTPStatus.INTERNAL_SERVER_ERROR)
        logging.exception(message)
        return results_dict

    status_code = response.status_code
    results_dict['status_code'] = status_code

    if status_code != HTTPStatus.OK:
        message = 'Encountered error: Metadata request failed'
        results_dict['msg'] = message
        logging.error(message)
        return results_dict

    try:
        table_data_raw: dict = response.json()

        # Ideally the response should include 'key' to begin with
        table_data_raw['key'] = table_key

        results_dict['tableData'] = marshall_table_full(table_data_raw)
        results_dict['msg'] = 'Success'
        return results_dict
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        results_dict['msg'] = message
        logging.exception(message)
        # explicitly raise the exception which will trigger 500 api response
        results_dict['status_code'] = getattr(e, 'code', HTTPStatus.INTERNAL_SERVER_ERROR)
        return results_dict


@metadata_blueprint.route('/update_table_owner', methods=['PUT', 'DELETE'])
def update_table_owner() -> Response:

    @action_logging
    def _log_update_table_owner(*, table_key: str, method: str, owner: str) -> None:
        pass  # pragma: no cover

    try:
        args = request.get_json()
        table_key = get_query_param(args, 'key')
        owner = get_query_param(args, 'owner')

        table_endpoint = _get_table_endpoint()
        url = '{0}/{1}/owner/{2}'.format(table_endpoint, table_key, owner)
        method = request.method
        _log_update_table_owner(table_key=table_key, method=method, owner=owner)

        response = request_metadata(url=url, method=method)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Updated owner'
        else:
            message = 'There was a problem updating owner {0}'.format(owner)

        payload = jsonify({'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        payload = jsonify({'msg': 'Encountered exception: ' + str(e)})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/get_last_indexed')
def get_last_indexed() -> Response:
    """
    call the metadata service endpoint to get the last indexed timestamp of neo4j
    :return: a json output containing the last indexed timestamp, in unix epoch time, as 'timestamp'

    Schema Defined Here: https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/api/system.py
    """
    try:
        url = app.config['METADATASERVICE_BASE'] + LAST_INDEXED_ENDPOINT

        response = request_metadata(url=url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
            timestamp = response.json().get('neo4j_latest_timestamp')
        else:
            message = 'Timestamp Unavailable'
            timestamp = None

        payload = jsonify({'timestamp': timestamp, 'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        payload = jsonify({'timestamp': None, 'msg': 'Encountered exception: ' + str(e)})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/get_table_description', methods=['GET'])
def get_table_description() -> Response:
    try:
        table_endpoint = _get_table_endpoint()
        table_key = get_query_param(request.args, 'key')

        url = '{0}/{1}/description'.format(table_endpoint, table_key)

        response = request_metadata(url=url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
            description = response.json().get('description')
        else:
            message = 'Get table description failed'
            description = None

        payload = jsonify({'description': description, 'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        payload = jsonify({'description': None, 'msg': 'Encountered exception: ' + str(e)})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/get_column_description', methods=['GET'])
def get_column_description() -> Response:
    try:
        table_endpoint = _get_table_endpoint()
        table_key = get_query_param(request.args, 'key')

        column_name = get_query_param(request.args, 'column_name')

        url = '{0}/{1}/column/{2}/description'.format(table_endpoint, table_key, column_name)

        response = request_metadata(url=url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
            description = response.json().get('description')
        else:
            message = 'Get column description failed'
            description = None

        payload = jsonify({'description': description, 'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        payload = jsonify({'description': None, 'msg': 'Encountered exception: ' + str(e)})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/put_table_description', methods=['PUT'])
def put_table_description() -> Response:

    @action_logging
    def _log_put_table_description(*, table_key: str, description: str, source: str) -> None:
        pass  # pragma: no cover

    try:
        args = request.get_json()
        table_endpoint = _get_table_endpoint()

        table_key = get_query_param(args, 'key')

        description = get_query_param(args, 'description')
        src = get_query_param(args, 'source')

        url = '{0}/{1}/description'.format(table_endpoint, table_key)
        _log_put_table_description(table_key=table_key, description=description, source=src)

        response = request_metadata(url=url, method='PUT', data=json.dumps({'description': description}))
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
        else:
            message = 'Update table description failed'

        payload = jsonify({'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        payload = jsonify({'msg': 'Encountered exception: ' + str(e)})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/put_column_description', methods=['PUT'])
def put_column_description() -> Response:

    @action_logging
    def _log_put_column_description(*, table_key: str, column_name: str, description: str, source: str) -> None:
        pass  # pragma: no cover

    try:
        args = request.get_json()

        table_key = get_query_param(args, 'key')
        table_endpoint = _get_table_endpoint()

        column_name = get_query_param(args, 'column_name')
        description = get_query_param(args, 'description')

        src = get_query_param(args, 'source')

        url = '{0}/{1}/column/{2}/description'.format(table_endpoint, table_key, column_name)
        _log_put_column_description(table_key=table_key, column_name=column_name, description=description, source=src)

        response = request_metadata(url=url, method='PUT', data=json.dumps({'description': description}))
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
        else:
            message = 'Update column description failed'

        payload = jsonify({'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        payload = jsonify({'msg': 'Encountered exception: ' + str(e)})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/tags')
def get_tags() -> Response:
    """
    call the metadata service endpoint to get the list of all tags from neo4j
    :return: a json output containing the list of all tags, as 'tags'

    Schema Defined Here: https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/api/tag.py
    """
    try:
        url = app.config['METADATASERVICE_BASE'] + TAGS_ENDPOINT
        response = request_metadata(url=url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
            tags = response.json().get('tag_usages')
        else:
            message = 'Encountered error: Tags Unavailable'
            logging.error(message)
            tags = []

        payload = jsonify({'tags': tags, 'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        payload = jsonify({'tags': [], 'msg': message})
        logging.exception(message)
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/update_table_tags', methods=['PUT', 'DELETE'])
def update_table_tags() -> Response:

    @action_logging
    def _log_update_table_tags(*, table_key: str, method: str, tag: str) -> None:
        pass  # pragma: no cover

    try:
        args = request.get_json()
        method = request.method

        table_endpoint = _get_table_endpoint()
        table_key = get_query_param(args, 'key')

        tag = get_query_param(args, 'tag')

        url = f'{table_endpoint}/{table_key}/tag/{tag}'

        _log_update_table_tags(table_key=table_key, method=method, tag=tag)

        response = request_metadata(url=url, method=method)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
        else:
            message = f'Encountered error: {method} table tag failed'
            logging.error(message)

        payload = jsonify({'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        payload = jsonify({'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/update_dashboard_tags', methods=['PUT', 'DELETE'])
def update_dashboard_tags() -> Response:

    @action_logging
    def _log_update_dashboard_tags(*, uri_key: str, method: str, tag: str) -> None:
        pass  # pragma: no cover

    try:
        args = request.get_json()
        method = request.method

        dashboard_endpoint = _get_dashboard_endpoint()
        uri_key = get_query_param(args, 'key')
        tag = get_query_param(args, 'tag')
        url = f'{dashboard_endpoint}/{uri_key}/tag/{tag}'

        _log_update_dashboard_tags(uri_key=uri_key, method=method, tag=tag)

        response = request_metadata(url=url, method=method)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
        else:
            message = f'Encountered error: {method} dashboard tag failed'
            logging.error(message)

        payload = jsonify({'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        payload = jsonify({'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/user', methods=['GET'])
def get_user() -> Response:

    @action_logging
    def _log_get_user(*, user_id: str, index: Optional[int], source: Optional[str]) -> None:
        pass  # pragma: no cover

    try:
        user_id = get_query_param(request.args, 'user_id')
        index = request.args.get('index', None)
        source = request.args.get('source', None)

        url = '{0}{1}/{2}'.format(app.config['METADATASERVICE_BASE'], USER_ENDPOINT, user_id)
        _log_get_user(user_id=user_id, index=index, source=source)

        response = request_metadata(url=url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
        else:
            message = 'Encountered error: failed to fetch user with user_id: {0}'.format(user_id)
            logging.error(message)

        payload = {
            'msg': message,
            'user': dump_user(load_user(response.json())),
        }
        return make_response(jsonify(payload), status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        payload = jsonify({'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/user/bookmark', methods=['GET'])
def get_bookmark() -> Response:
    """
    Call metadata service to fetch a specified user's bookmarks.
    If no 'user_id' is specified, it will fetch the logged-in user's bookmarks
    :param user_id: (optional) the user whose bookmarks are fetched.
    :return: a JSON object with an array of bookmarks under 'bookmarks' key
    """
    try:
        user_id = request.args.get('user_id')
        if user_id is None:
            if app.config['AUTH_USER_METHOD']:
                user_id = app.config['AUTH_USER_METHOD'](app).user_id
            else:
                raise Exception('AUTH_USER_METHOD is not configured')

        url = '{0}{1}/{2}/follow/'.format(app.config['METADATASERVICE_BASE'], USER_ENDPOINT, user_id)

        response = request_metadata(url=url, method=request.method)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
            tables = response.json().get('table')
            table_bookmarks = [marshall_table_partial(table) for table in tables]
            dashboards = response.json().get('dashboard', [])
            dashboard_bookmarks = [marshall_dashboard_partial(dashboard) for dashboard in dashboards]
        else:
            message = f'Encountered error: failed to get bookmark for user_id: {user_id}'
            logging.error(message)
            table_bookmarks = []
            dashboard_bookmarks = []

        all_bookmarks = {
            'table': table_bookmarks,
            'dashboard': dashboard_bookmarks
        }
        return make_response(jsonify({'msg': message, 'bookmarks': all_bookmarks}), status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        return make_response(jsonify({'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/user/bookmark', methods=['PUT', 'DELETE'])
def update_bookmark() -> Response:
    """
    Call metadata service to PUT or DELETE a bookmark
    Params
    :param type: Resource type for the bookmarked item. e.g. 'table'
    :param key: Resource key for the bookmarked item.
    :return:
    """

    @action_logging
    def _log_update_bookmark(*, resource_key: str, resource_type: str, method: str) -> None:
        pass  # pragma: no cover

    try:
        if app.config['AUTH_USER_METHOD']:
            user = app.config['AUTH_USER_METHOD'](app)
        else:
            raise Exception('AUTH_USER_METHOD is not configured')

        args = request.get_json()
        resource_type = get_query_param(args, 'type')
        resource_key = get_query_param(args, 'key')

        url = '{0}{1}/{2}/follow/{3}/{4}'.format(app.config['METADATASERVICE_BASE'],
                                                 USER_ENDPOINT,
                                                 user.user_id,
                                                 resource_type,
                                                 resource_key)

        _log_update_bookmark(resource_key=resource_key, resource_type=resource_type, method=request.method)

        response = request_metadata(url=url, method=request.method)
        status_code = response.status_code

        return make_response(jsonify({'msg': 'success', 'response': response.json()}), status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        return make_response(jsonify({'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/user/read', methods=['GET'])
def get_user_read() -> Response:
    """
    Calls metadata service to GET read/frequently used resources
    :return: a JSON object with an array of read resources
    """
    try:
        user_id = get_query_param(request.args, 'user_id')

        url = '{0}{1}/{2}/read/'.format(app.config['METADATASERVICE_BASE'],
                                        USER_ENDPOINT,
                                        user_id)
        response = request_metadata(url=url, method=request.method)
        status_code = response.status_code
        read_tables_raw = response.json().get('table')
        read_tables = [marshall_table_partial(table) for table in read_tables_raw]
        return make_response(jsonify({'msg': 'success', 'read': read_tables}), status_code)

    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        return make_response(jsonify({'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/user/own', methods=['GET'])
def get_user_own() -> Response:
    """
    Calls metadata service to GET owned resources
    :return: a JSON object with an array of owned resources
    """
    try:
        user_id = get_query_param(request.args, 'user_id')

        url = '{0}{1}/{2}/own/'.format(app.config['METADATASERVICE_BASE'],
                                       USER_ENDPOINT,
                                       user_id)
        response = request_metadata(url=url, method=request.method)
        status_code = response.status_code
        owned_tables_raw = response.json().get('table')
        owned_tables = [marshall_table_partial(table) for table in owned_tables_raw]
        dashboards = response.json().get('dashboard', [])
        owned_dashboards = [marshall_dashboard_partial(dashboard) for dashboard in dashboards]
        all_owned = {
            'table': owned_tables,
            'dashboard': owned_dashboards
        }
        return make_response(jsonify({'msg': 'success', 'own': all_owned}), status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        return make_response(jsonify({'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/dashboard', methods=['GET'])
def get_dashboard_metadata() -> Response:
    """
    Call metadata service endpoint to fetch specified dashboard metadata
    :return:
    """
    @action_logging
    def _get_dashboard_metadata(*, uri: str, index: int, source: str) -> None:
        pass  # pragma: no cover

    try:
        uri = get_query_param(request.args, 'uri')
        index = request.args.get('index', None)
        source = request.args.get('source', None)
        _get_dashboard_metadata(uri=uri, index=index, source=source)

        url = f'{app.config["METADATASERVICE_BASE"]}{DASHBOARD_ENDPOINT}/{uri}'

        response = request_metadata(url=url, method=request.method)
        dashboard = marshall_dashboard_full(response.json())
        status_code = response.status_code
        return make_response(jsonify({'msg': 'success', 'dashboard': dashboard}), status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        return make_response(jsonify({'dashboard': {}, 'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)


@metadata_blueprint.route('/table/<path:table_key>/dashboards', methods=['GET'])
def get_related_dashboard_metadata(table_key: str) -> Response:
    """
    Call metadata service endpoint to fetch related dashboard metadata
    :return:
    """
    try:
        url = f'{app.config["METADATASERVICE_BASE"]}{TABLE_ENDPOINT}/{table_key}/dashboard/'
        results_dict = _get_related_dashboards_metadata(url=url)
        return make_response(jsonify(results_dict), results_dict.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR))
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        return make_response(jsonify({'dashboards': [], 'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)


@action_logging
def _get_related_dashboards_metadata(*, url: str) -> Dict[str, Any]:

    results_dict = {
        'dashboards': {},
        'msg': '',
    }

    try:
        response = request_metadata(url=url)
    except ValueError as e:
        # envoy client BadResponse is a subclass of ValueError
        message = 'Encountered exception: ' + str(e)
        results_dict['msg'] = message
        results_dict['status_code'] = getattr(e, 'code', HTTPStatus.INTERNAL_SERVER_ERROR)
        logging.exception(message)
        return results_dict

    status_code = response.status_code
    results_dict['status_code'] = status_code

    if status_code != HTTPStatus.OK:
        message = 'Encountered error: Related Dashboard Metadata request failed'
        results_dict['msg'] = message
        logging.error(message)
        return results_dict

    try:
        dashboard_data_raw = response.json().get('dashboards', [])
        return {
            'dashboards': [marshall_dashboard_partial(dashboard) for dashboard in dashboard_data_raw],
            'msg': 'Success',
            'status_code': status_code
        }
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        results_dict['msg'] = message
        logging.exception(message)
        # explicitly raise the exception which will trigger 500 api response
        results_dict['status_code'] = getattr(e, 'code', HTTPStatus.INTERNAL_SERVER_ERROR)
        return results_dict
