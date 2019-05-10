import logging

from http import HTTPStatus
from typing import Any, Dict

from flask import Response, jsonify, make_response, request
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_application.log.action_log import action_logging

from amundsen_application.models.user import load_user, dump_user

from amundsen_application.api.utils.request_utils import get_query_param, request_metadata


LOGGER = logging.getLogger(__name__)


metadata_blueprint = Blueprint('metadata', __name__, url_prefix='/api/metadata/v0')

TABLE_ENDPOINT = '/table'
LAST_INDEXED_ENDPOINT = '/latest_updated_ts'
POPULAR_TABLES_ENDPOINT = '/popular_tables/'
TAGS_ENDPOINT = '/tags/'
USER_ENDPOINT = '/user'


def _get_table_endpoint() -> str:
    table_endpoint = app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT
    if table_endpoint is None:
        raise Exception('An request endpoint for table resources must be configured')
    return table_endpoint


def _get_table_key(args: Dict) -> str:
    db = get_query_param(args, 'db')
    cluster = get_query_param(args, 'cluster')
    schema = get_query_param(args, 'schema')
    table = get_query_param(args, 'table')
    table_key = '{db}://{cluster}.{schema}/{table}'.format(**locals())
    return table_key


@metadata_blueprint.route('/popular_tables', methods=['GET'])
def popular_tables() -> Response:
    """
    call the metadata service endpoint to get the current popular tables
    :return: a json output containing an array of popular table metadata as 'popular_tables'

    Schema Defined Here:
    https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/api/popular_tables.py
    """
    def _map_results(result: Dict) -> Dict:
        table_name = result.get('table_name')
        schema_name = result.get('schema')
        cluster = result.get('cluster')
        db = result.get('database')
        return {
            'name': table_name,
            'schema_name': schema_name,
            'cluster': cluster,
            'database': db,
            'description': result.get('table_description'),
            'key': '{0}://{1}.{2}/{3}'.format(db, cluster, schema_name, table_name),
            'type': 'table',
        }

    try:
        url = app.config['METADATASERVICE_BASE'] + POPULAR_TABLES_ENDPOINT
        response = request_metadata(url=url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
            response_list = response.json().get('popular_tables')
            top4 = response_list[0:min(len(response_list), app.config['POPULAR_TABLE_COUNT'])]
            popular_tables = [_map_results(result) for result in top4]
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
        table_key = _get_table_key(request.args)
        list_item_index = get_query_param(request.args, 'index')
        list_item_source = get_query_param(request.args, 'source')

        results_dict = _get_table_metadata(table_key=table_key, index=list_item_index, source=list_item_source)
        return make_response(jsonify(results_dict), results_dict.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR))
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        return make_response(jsonify({'tableData': {}, 'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)


def _get_partition_data(watermarks: Dict) -> Dict:
    if watermarks:
        high_watermark = next(filter(lambda x: x['watermark_type'] == 'high_watermark', watermarks))
        if high_watermark:
            return {
                'is_partitioned': True,
                'key': high_watermark['partition_key'],
                'value': high_watermark['partition_value']
            }
    return {
        'is_partitioned': False
    }


@action_logging
def _get_table_metadata(*, table_key: str, index: int, source: str) -> Dict[str, Any]:

    def _map_user_object_to_schema(u: Dict) -> Dict:
        return dump_user(load_user(u))

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
        # Filter and parse the response dictionary from the metadata service
        params = [
            'columns',
            'cluster',
            'database',
            'owners',
            'is_view',
            'schema',
            'table_description',
            'table_name',
            'table_readers',
            'table_writer',
            'tags',
            'watermarks',
            'source',
        ]

        results = {key: response.json().get(key, None) for key in params}

        is_editable = results['schema'] not in app.config['UNEDITABLE_SCHEMAS']
        results['is_editable'] = is_editable

        # In the list of owners, sanitize each entry
        results['owners'] = [_map_user_object_to_schema(owner) for owner in results['owners']]

        # In the list of reader_objects, sanitize the reader value on each entry
        readers = results['table_readers']
        for reader_object in readers:
            reader_object['reader'] = _map_user_object_to_schema(reader_object['reader'])

        # If order is provided, we sort the column based on the pre-defined order
        if app.config['COLUMN_STAT_ORDER']:
            columns = results['columns']
            for col in columns:
                # the stat_type isn't defined in COLUMN_STAT_ORDER, we just use the max index for sorting
                col['stats'].sort(key=lambda x: app.config['COLUMN_STAT_ORDER'].
                                  get(x['stat_type'], len(app.config['COLUMN_STAT_ORDER'])))
                col['is_editable'] = is_editable

        # Temp code to make 'partition_key' and 'partition_value' part of the table
        results['partition'] = _get_partition_data(results['watermarks'])

        results_dict['tableData'] = results
        results_dict['msg'] = 'Success'
        return results_dict
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        results_dict['msg'] = message
        logging.exception(message)
        # explicitly raise the exception which will trigger 500 api response
        results_dict['status_code'] = getattr(e, 'code', HTTPStatus.INTERNAL_SERVER_ERROR)
        return results_dict


@action_logging
def _update_table_owner(*, table_key: str, method: str, owner: str) -> Dict[str, str]:
    try:
        table_endpoint = _get_table_endpoint()
        url = '{0}/{1}/owner/{2}'.format(table_endpoint, table_key, owner)
        request_metadata(url=url, method=method)

        # TODO: Figure out a way to get this payload from flask.jsonify which wraps with app's response_class
        return {'msg': 'Updated owner'}
    except Exception as e:
        return {'msg': 'Encountered exception: ' + str(e)}


@metadata_blueprint.route('/update_table_owner', methods=['PUT', 'DELETE'])
def update_table_owner() -> Response:
    try:
        args = request.get_json()
        table_key = _get_table_key(args)
        owner = get_query_param(args, 'owner')

        payload = jsonify(_update_table_owner(table_key=table_key, method=request.method, owner=owner))
        return make_response(payload, HTTPStatus.OK)
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
        table_key = _get_table_key(request.args)

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
        table_key = _get_table_key(request.args)

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

        table_key = _get_table_key(args)

        description = get_query_param(args, 'description')
        description = ' '.join(description.split())
        src = get_query_param(args, 'source')

        url = '{0}/{1}/description/{2}'.format(table_endpoint, table_key, description)
        _log_put_table_description(table_key=table_key, description=description, source=src)

        response = request_metadata(url=url, method='PUT')
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

        table_key = _get_table_key(args)
        table_endpoint = _get_table_endpoint()

        column_name = get_query_param(args, 'column_name')
        description = get_query_param(args, 'description')
        description = ' '.join(description.split())

        src = get_query_param(args, 'source')

        url = '{0}/{1}/column/{2}/description/{3}'.format(table_endpoint, table_key, column_name, description)
        _log_put_column_description(table_key=table_key, column_name=column_name, description=description, source=src)

        response = request_metadata(url=url, method='PUT')
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
        table_key = _get_table_key(args)

        tag = get_query_param(args, 'tag')

        url = '{0}/{1}/tag/{2}'.format(table_endpoint, table_key, tag)

        _log_update_table_tags(table_key=table_key, method=method, tag=tag)

        response = request_metadata(url=url, method=method)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
        else:
            message = 'Encountered error: {0} tag failed'.format(method)
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
    def _log_get_user(*, user_id: str) -> None:
        pass  # pragma: no cover

    try:
        user_id = get_query_param(request.args, 'user_id')
        url = '{0}{1}/{2}'.format(app.config['METADATASERVICE_BASE'], USER_ENDPOINT, user_id)

        _log_get_user(user_id=user_id)

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
