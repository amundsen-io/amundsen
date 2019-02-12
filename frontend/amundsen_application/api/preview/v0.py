import json
import logging

from http import HTTPStatus
from pkg_resources import iter_entry_points

from flask import Response, jsonify, make_response, request
from flask.blueprints import Blueprint

from amundsen_application.models.preview_data import PreviewDataSchema

LOGGER = logging.getLogger(__name__)

# TODO: Blueprint classes might be the way to go
PREVIEW_CLIENT_CLASS = None
PREVIEW_CLIENT_INSTANCE = None

# get the preview_client_class from the python entry point
for entry_point in iter_entry_points(group='preview_client', name='table_preview_client_class'):
    preview_client_class = entry_point.load()
    if preview_client_class is not None:
        PREVIEW_CLIENT_CLASS = preview_client_class

preview_blueprint = Blueprint('preview', __name__, url_prefix='/api/preview/v0')


@preview_blueprint.route('/', methods=['POST'])
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
