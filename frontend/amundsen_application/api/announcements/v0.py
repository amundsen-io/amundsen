# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from http import HTTPStatus
from pkg_resources import iter_entry_points

from flask import Response, jsonify, make_response
from flask.blueprints import Blueprint

LOGGER = logging.getLogger(__name__)

# TODO: Blueprint classes might be the way to go
ANNOUNCEMENT_CLIENT_CLASS = None
ANNOUNCEMENT_CLIENT_INSTANCE = None

# get the announcement_client_class from the python entry point
for entry_point in iter_entry_points(group='announcement_client', name='announcement_client_class'):
    announcement_client_class = entry_point.load()
    if announcement_client_class is not None:
        ANNOUNCEMENT_CLIENT_CLASS = announcement_client_class

announcements_blueprint = Blueprint('announcements', __name__, url_prefix='/api/announcements/v0')


@announcements_blueprint.route('/', methods=['GET'])
def get_announcements() -> Response:
    global ANNOUNCEMENT_CLIENT_INSTANCE
    try:
        if ANNOUNCEMENT_CLIENT_INSTANCE is None and ANNOUNCEMENT_CLIENT_CLASS is not None:
            ANNOUNCEMENT_CLIENT_INSTANCE = ANNOUNCEMENT_CLIENT_CLASS()

        if ANNOUNCEMENT_CLIENT_INSTANCE is None:
            payload = jsonify({'posts': [], 'msg': 'A client for retrieving announcements must be configured'})
            return make_response(payload, HTTPStatus.NOT_IMPLEMENTED)

        return ANNOUNCEMENT_CLIENT_INSTANCE._get_posts()
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        payload = jsonify({'posts': [], 'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)
