# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from pkg_resources import iter_entry_points

from http import HTTPStatus

from flask import Response, jsonify, make_response, request, current_app as app
from flask.blueprints import Blueprint
from marshmallow import ValidationError
from werkzeug.utils import import_string

from amundsen_application.models.ai import GPTResponseSchema
from amundsen_application.api.utils.request_utils import get_query_param

LOGGER = logging.getLogger(__name__)

AI_CLIENT_CLASS = None
AI_CLIENT_INSTANCE = None


ai_blueprint = Blueprint('ai', __name__, url_prefix='/api/ai/v0')


@ai_blueprint.route('/get_gpt_response', methods=['GET'])
def get_gpt_response() -> Response:
    global AI_CLIENT_INSTANCE
    global AI_CLIENT_CLASS
    try:
        LOGGER.info(f"get_gpt_response")
        if AI_CLIENT_INSTANCE is None:
            if (app.config['AI_CLIENT_ENABLED'] and
                app.config['AI_CLIENT'] is not None):
                AI_CLIENT_CLASS = import_string(app.config['AI_CLIENT'])
                AI_CLIENT_INSTANCE = AI_CLIENT_CLASS()
                LOGGER.info(f"AI_CLIENT_INSTANCE={AI_CLIENT_INSTANCE}")
            else:
                LOGGER.info(f"A client for the AI feature must be configured")
                payload = jsonify({'gptResponse': {}, 'msg': 'A client for the AI feature must be configured'})
                return make_response(payload, HTTPStatus.NOT_IMPLEMENTED)

        prompt = get_query_param(request.args, 'prompt')
        response = AI_CLIENT_INSTANCE.get_gpt_response(prompt=prompt)
        status_code = response.status_code
        LOGGER.info(f"response.data={response.data}")

        gpt_response = json.loads(response.data).get('gpt_response')
        LOGGER.info(f"gpt_response={gpt_response}")
        if status_code == HTTPStatus.OK:
            # validate the returned table preview data
            try:
                data = GPTResponseSchema().load(gpt_response)
                LOGGER.info(f"data={data}")
                payload = jsonify({'gptResponse': data, 'msg': 'Success'})
                LOGGER.info(f"payload={payload}")
            except ValidationError as err:
                logging.error('GPT response dump returned errors: ' + str(err.messages))
                raise Exception('The AI client did not return a valid GPTResponse object')
        else:
            message = 'Encountered error: AI client request failed with code ' + str(status_code)
            logging.error(message)
            # only necessary to pass the error text
            payload = jsonify({'gptResponse': {'error_text': gpt_response.get('error_text', '')}, 'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        message = f'Encountered exception: {str(e)}'
        logging.exception(message)
        payload = jsonify({'gptResponse': {}, 'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)
