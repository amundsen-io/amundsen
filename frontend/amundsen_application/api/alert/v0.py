# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import json

from http import HTTPStatus
from typing import cast


from flask import Response, jsonify, make_response, request, current_app as app
from flask.blueprints import Blueprint
from marshmallow import ValidationError
from werkzeug.utils import import_string

from amundsen_application.api.utils.request_utils import get_query_param
from amundsen_application.base.base_notice_client import BaseNoticeClient

LOGGER = logging.getLogger(__name__)
ALERT_CLIENT_INSTANCE = None

alert_blueprint = Blueprint('alert', __name__, url_prefix='/api/alert/v0')

def get_alert_client() -> BaseNoticeClient:
    global ALERT_CLIENT_INSTANCE
    if ALERT_CLIENT_INSTANCE is None and app.config['ALERT_CLIENT'] is not None:
        alert_client_class = import_string(app.config['ALERT_CLIENT'])
        ALERT_CLIENT_INSTANCE = alert_client_class()  # TODO how to pass it the private Lyft data health sub-client?
        # TODO NB private QualityChecksClient doesn't take any constructor args
    return cast(BaseNoticeClient, ALERT_CLIENT_INSTANCE)

@alert_blueprint.route('/table/summary', methods=['GET'])  # TODO call it something other than 'summary'?
def get_table_alerts_summary() -> Response:
    global ALERT_CLIENT_INSTANCE
    try:
        client = get_alert_client()
        if client is not None:
            return _get_table_alerts_summary_client()
        payload = jsonify({'placeholder': 'this feature is not implemented'})
        return make_response(payload, HTTPStatus.NOT_IMPLEMENTED)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        payload = jsonify({'alerts': {}, 'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)

# TODO {'payload' (optional): {
#   ...'link': the url string
# }}

def _get_table_alerts_summary_client() -> Response:
    client = get_alert_client()
    table_key = get_query_param(request.args, 'key')
    response = client.get_table_notices_summary(table_key=table_key)
    status_code = response.status_code
    if status_code == HTTPStatus.OK:
        try:
            alerts = json.loads(response.data).get('alerts')
            payload = jsonify({'alerts': alerts, 'msg': 'Success'})
        except ValidationError as err:  # TODO what exactly is raising ValidationError? Sure this isn't specific to QualityClient?
            LOGGER.error(f'Table alerts data dump returned errors: {err.messages}')  # TODO too blindly copied from QualityClient?
            raise Exception('The preview client did not return a valid TableAlert object')  # TODO match to Alerts stuff wording
    else:
        message = f'Encountered error: Alert client request failed with code {status_code}'
        LOGGER.error(message)
        payload = jsonify({'alerts': {}, 'msg': message})

