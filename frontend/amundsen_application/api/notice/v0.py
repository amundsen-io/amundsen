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
NOTICE_CLIENT_INSTANCE = None

notices_blueprint = Blueprint('notices', __name__, url_prefix='/api/notices/v0')


def get_notice_client() -> BaseNoticeClient:
    global NOTICE_CLIENT_INSTANCE
    if NOTICE_CLIENT_INSTANCE is None and app.config['NOTICE_CLIENT'] is not None:
        notice_client_class = import_string(app.config['NOTICE_CLIENT'])
        NOTICE_CLIENT_INSTANCE = notice_client_class()
    return cast(BaseNoticeClient, NOTICE_CLIENT_INSTANCE)


@notices_blueprint.route('/table', methods=['GET'])
def get_table_notices_summary() -> Response:
    global NOTICE_CLIENT_INSTANCE
    try:
        client = get_notice_client()
        if client is not None:
            return _get_table_notices_summary_client()
        payload = jsonify({'notices': {}, 'msg': 'A client for retrieving resource notices must be configured'})
        return make_response(payload, HTTPStatus.NOT_IMPLEMENTED)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        LOGGER.exception(message)
        payload = jsonify({'notices': {}, 'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


def _get_table_notices_summary_client() -> Response:
    client = get_notice_client()
    table_key = get_query_param(request.args, 'key')
    response = client.get_table_notices_summary(table_key=table_key)
    status_code = response.status_code
    if status_code == HTTPStatus.OK:
        try:
            notices = json.loads(response.data).get('notices')
            payload = jsonify({'notices': notices, 'msg': 'Success'})
        except ValidationError as err:
            LOGGER.info('Notices data dump returned errors: ' + str(err.messages))
            raise Exception(f"Notices client didn't return a valid ResourceNotice object. {err}")
    else:
        message = f'Encountered error: Notice client request failed with code {status_code}'
        LOGGER.error(message)
        payload = jsonify({'notices': {}, 'msg': message})
    return make_response(payload, status_code)
