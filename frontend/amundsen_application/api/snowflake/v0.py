# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import json

from http import HTTPStatus
from typing import Any, Dict, Optional

from flask import Response, jsonify, make_response, request
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_common.entity.resource_type import ResourceType, to_label
from amundsen_common.models.search import UpdateDocumentRequestSchema, UpdateDocumentRequest

from amundsen_application.log.action_log import action_logging

from amundsen_application.models.user import load_user, dump_user

from amundsen_application.api.utils.metadata_utils import is_table_editable, marshall_table_partial, \
    marshall_table_full, marshall_dashboard_partial, marshall_dashboard_full, marshall_feature_full, \
    marshall_lineage_table, TableUri
from amundsen_application.api.utils.request_utils import get_query_param, request_metadata

from amundsen_application.api.utils.search_utils import execute_search_document_request


LOGGER = logging.getLogger(__name__)


snowflake_blueprint = Blueprint('snowflake', __name__, url_prefix='/api/snowflake/v0')

SNOWFLAKE_TABLE_ENDPOINT = '/snowflake/table'


def _get_snowflake_table_endpoint() -> str:
    metadata_service_base = app.config['METADATASERVICE_BASE']
    if metadata_service_base is None:
        raise Exception('METADATASERVICE_BASE must be configured')
    return metadata_service_base + SNOWFLAKE_TABLE_ENDPOINT
    
@snowflake_blueprint.route('/get_snowflake_table_shares', methods=['GET'])
def get_snowflake_table_shares() -> Response:
    try:
        snowflake_table_endpoint = _get_snowflake_table_endpoint()
        table_uri = get_query_param(request.args, 'tableUri')

        url = '{0}/{1}/shares'.format(snowflake_table_endpoint, table_uri)

        response = request_metadata(url=url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            message = 'Success'
            snowflake_table_shares = response.json().get('snowflake_table_shares')
        else:
            message = 'Encountered error: Snowflake Table Shares Unavailable'
            logging.error(message)
            snowflake_table_shares = []

        payload = jsonify({'snowflake_table_shares': snowflake_table_shares, 'msg': message})
        return make_response(payload, status_code)
    except Exception as e:
        payload = jsonify({'snowflake_table_shares': [], 'msg': 'Encountered exception: ' + str(e)})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)