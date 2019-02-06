import json
import logging

from http import HTTPStatus
from pkg_resources import iter_entry_points

from flask import Response, jsonify, make_response, request
from flask import current_app as app
from flask.blueprints import Blueprint

# from amundsen_application.log.action_log import action_logging

from amundsen_application.models.preview_data import PreviewDataSchema
from amundsen_application.models.user import load_user

LOGGER = logging.getLogger(__name__)

# TODO: Blueprint classes might be the way to go
PREVIEW_CLIENT_CLASS = None
PREVIEW_CLIENT_INSTANCE = None
ANNOUNCEMENT_CLIENT_CLASS = None
ANNOUNCEMENT_CLIENT_INSTANCE = None

# get the preview_client_class from the python entry point
for entry_point in iter_entry_points(group='preview_client', name='table_preview_client_class'):
    preview_client_class = entry_point.load()
    if preview_client_class is not None:
        PREVIEW_CLIENT_CLASS = preview_client_class

# get the announcement_client_class from the python entry point
for entry_point in iter_entry_points(group='announcement_client', name='announcement_client_class'):
    announcement_client_class = entry_point.load()
    if announcement_client_class is not None:
        ANNOUNCEMENT_CLIENT_CLASS = announcement_client_class

blueprint = Blueprint('api', __name__, url_prefix='/api')


@blueprint.route('/current_user', methods=['GET'])
def current_user() -> Response:
    if (app.config['CURRENT_USER_METHOD']):
        user = app.config['CURRENT_USER_METHOD'](app)
    else:
        user = load_user({'display_name': '*'})

    return user.to_json()


@blueprint.route('/preview', methods=['POST'])
def get_table_preview() -> Response:
    # TODO: Want to further separate this file into more blueprints, perhaps a Blueprint class is the way to go
    global PREVIEW_CLIENT_INSTANCE
    try:
        if PREVIEW_CLIENT_INSTANCE is None and PREVIEW_CLIENT_CLASS is not None:
            PREVIEW_CLIENT_INSTANCE = PREVIEW_CLIENT_CLASS()

        if PREVIEW_CLIENT_INSTANCE is None:
            payload = jsonify({'previewData': {}, 'msg': 'A client for the preview feature must be configured'})
            return make_response(payload, HTTPStatus.NOT_IMPLEMENTED)

        # request table preview data
        response = PREVIEW_CLIENT_INSTANCE.get_preview_data(params=request.get_json())
        status_code = response.status_code

        preview_data = json.loads(response.data).get('preview_data')
        if status_code == HTTPStatus.OK:
            # validate the returned table preview data
            data, errors = PreviewDataSchema().load(preview_data)
            if not errors:
                payload = jsonify({'previewData': data, 'msg': 'Success'})
            else:
                logging.error('Preview data dump returned errors: ' + str(errors))
                raise Exception('The preview client did not return a valid PreviewData object')
        else:
            message = 'Encountered error: Preview client request failed with code ' + str(status_code)
            logging.error(message)
            # only necessary to pass the error text
            payload = jsonify({'previewData': {'error_text': preview_data.get('error_text', '')}, 'msg': message})

        return make_response(payload, status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        payload = jsonify({'previewData': {}, 'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)


@blueprint.route('/announcements', methods=['GET'])
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
