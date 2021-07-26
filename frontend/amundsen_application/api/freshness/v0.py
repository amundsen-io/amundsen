# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging

from http import HTTPStatus

from flask import Response, jsonify, make_response, request, current_app as app
from flask.blueprints import Blueprint
from marshmallow import ValidationError
from werkzeug.utils import import_string

from amundsen_application.models.preview_data import PreviewDataSchema
from amundsen_application.api.metadata.v0 import _get_table_metadata

LOGGER = logging.getLogger(__name__)
DATA_FRESHNESS_CLIENT_CLASS = None
DATA_FRESHNESS_CLIENT_INSTANCE = None

freshness_blueprint = Blueprint('freshness', __name__, url_prefix='/api/freshness/v0')


@freshness_blueprint.route('/', methods=['POST'])
def get_table_freshness() -> Response:
    global DATA_FRESHNESS_CLIENT_INSTANCE
    global DATA_FRESHNESS_CLIENT_CLASS

    try:
        if DATA_FRESHNESS_CLIENT_INSTANCE is None:
            if (app.config['DATA_FRESHNESS_CLIENT_ENABLED']
                    and app.config['DATA_FRESHNESS_CLIENT'] is not None):
                DATA_FRESHNESS_CLIENT_CLASS = import_string(app.config['DATA_FRESHNESS_CLIENT'])
                DATA_FRESHNESS_CLIENT_INSTANCE = DATA_FRESHNESS_CLIENT_CLASS()
            else:
                payload = jsonify({'freshnessData': {'error_text': 'A client for the freshness must be configured'}})
                return make_response(payload, HTTPStatus.NOT_IMPLEMENTED)

        # get table metadata and pass to data_freshness_client
        # data_freshness_client need to check if the table has any column
        # that can be used to as freshness indicator
        params = request.get_json()
        if not all(param in params for param in ['database', 'cluster', 'schema', 'tableName']):
            payload = jsonify({'freshnessData': {'error_text': 'Missing parameters in request payload'}})
            return make_response(payload, HTTPStatus.FORBIDDEN)

        table_key = f'{params["database"]}://{params["cluster"]}.{params["schema"]}/{params["tableName"]}'
        # the index and source parameters are not referenced inside the function
        table_metadata = _get_table_metadata(table_key=table_key, index=0, source='')

        response = DATA_FRESHNESS_CLIENT_INSTANCE.get_freshness_data(params=table_metadata)
        status_code = response.status_code

        freshness_data = json.loads(response.data).get('freshness_data')
        if status_code == HTTPStatus.OK:
            # validate the returned data
            try:
                data = PreviewDataSchema().load(freshness_data)
                payload = jsonify({'freshnessData': data})
            except ValidationError as err:
                logging.error('Freshness data dump returned errors: ' + str(err.messages))
                raise Exception('The data freshness client did not return a valid object')
        else:
            message = 'Encountered error: Freshness client request failed with code ' + str(status_code)
            logging.error(message)
            # only necessary to pass the error text
            payload = jsonify({'freshnessData': {'error_text': freshness_data.get('error_text', '')}, 'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        message = f'Encountered exception: {str(e)}'
        logging.exception(message)
        payload = jsonify({'freshnessData': {}, 'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)
