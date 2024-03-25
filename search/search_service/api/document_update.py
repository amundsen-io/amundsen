# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
from http import HTTPStatus
from typing import Any, Tuple

from amundsen_common.models.search import UpdateDocumentRequestSchema
from flasgger import swag_from
from flask_restful import Resource, request

from search_service.proxy import get_proxy_client
from search_service.proxy.es_proxy_utils import RESOURCE_STR_MAPPING


class DocumentAPI(Resource):

    def __init__(self) -> None:
        self.proxy = get_proxy_client()
        self.request = UpdateDocumentRequestSchema().loads(json.dumps(request.get_json()))

    @swag_from('swagger_doc/search/document_post.yml')
    def post(self) -> Tuple[Any, int]:
        try:
            resp = self.proxy.update_document_by_key(resource_key=self.request.resource_key,
                                                     resource_type=RESOURCE_STR_MAPPING[self.request.resource_type],
                                                     field=self.request.field,
                                                     value=self.request.value,
                                                     operation=self.request.operation)
            return {'msg': resp}, HTTPStatus.OK
        except Exception as e:
            err_msg = f'Failed to update the field value: {e}'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self) -> Tuple[Any, int]:
        try:
            resp = self.proxy.delete_document_by_key(resource_key=self.request.resource_key,
                                                     resource_type=RESOURCE_STR_MAPPING[self.request.resource_type],
                                                     field=self.request.field,
                                                     value=self.request.value)
            return {'msg': resp}, HTTPStatus.OK
        except Exception as e:
            err_msg = f'Failed to delete the field value: {e}'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
