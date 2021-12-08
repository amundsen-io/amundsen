import json
from http import HTTPStatus

from flask_restful import Resource, request

from amundsen_common.models.search import UpdateDocumentRequestSchema
from search_service.proxy import get_proxy_client
from search_service.proxy.es_search_proxy import RESOURCE_STR_MAPPING


class DocumentAPI(Resource):

    def __init__(self) -> None:
        self.proxy = get_proxy_client()
        self.request = UpdateDocumentRequestSchema().loads(json.dumps(request.get_json()))

    def post(self):
        try:
            self.proxy.update_document_field(resource_key=self.request.resource_key,
                                             resource_type=RESOURCE_STR_MAPPING.get(self.request.resource_type),
                                             field=self.request.field,
                                             value=self.request.value,
                                             delete=False)
        except Exception as e:
            err_msg = f'Failed to update the field value: {e}'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self):
        try:
            self.proxy.update_document_field(resource_key=self.request.resource_key,
                                             resource_type=RESOURCE_STR_MAPPING.get(self.request.resource_type),
                                             field=self.request.field,
                                             value=self.request.value,
                                             delete=True)
        except Exception as e:
            err_msg = f'Failed to delete the field value: {e}'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
