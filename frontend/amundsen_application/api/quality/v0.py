# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging

from http import HTTPStatus
from typing import cast

from flask import Response, jsonify, make_response, request, current_app as app
from flask.blueprints import Blueprint
from marshmallow import ValidationError
from werkzeug.utils import import_string

from amundsen_application.api.utils.request_utils import get_query_param
from amundsen_application.base.base_quality_client import BaseQualityClient

LOGGER = logging.getLogger(__name__)
QUALITY_CLIENT_INSTANCE = None

quality_blueprint = Blueprint('quality', __name__, url_prefix='/api/quality/v0')


def get_quality_client() -> BaseQualityClient:
    global QUALITY_CLIENT_INSTANCE
    if QUALITY_CLIENT_INSTANCE is None and app.config['QUALITY_CLIENT'] is not None:
        quality_client_class = import_string(app.config['QUALITY_CLIENT'])
        QUALITY_CLIENT_INSTANCE = quality_client_class()
    return cast(BaseQualityClient, QUALITY_CLIENT_INSTANCE)


@quality_blueprint.route('/table/summary', methods=['GET'])
def get_table_quality_checks_summary() -> Response:
    global QUALITY_CLIENT_INSTANCE
    try:
        client = get_quality_client()
        if client is not None:
            return _get_dq_checks_summary_client()
        payload = jsonify({'checks': {}, 'msg': 'This feature is not implemented'})
        return make_response(payload, HTTPStatus.NOT_IMPLEMENTED)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        payload = jsonify({'checks': {}, 'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


def _get_dq_checks_summary_client() -> Response:
    client = get_quality_client()
    table_key = get_query_param(request.args, 'key')
    response = client.get_table_quality_checks_summary(table_key=table_key)
    status_code = response.status_code
    if status_code == HTTPStatus.OK:
        try:
            quality_checks = json.loads(response.data).get('checks')
            payload = jsonify({'checks': quality_checks, 'msg': 'Success'})
        except ValidationError as err:
            logging.error('Quality data dump returned errors: ' + str(err.messages))
            raise Exception('The preview client did not return a valid Quality Checks object')
    else:
        message = 'Encountered error: Quality client request failed with code ' + str(status_code)
        logging.error(message)
        # only necessary to pass the error text
        payload = jsonify({'checks': {}, 'msg': message})
    return make_response(payload, status_code)
