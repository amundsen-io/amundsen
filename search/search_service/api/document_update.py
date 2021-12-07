import json
import logging
from http import HTTPStatus

from flask_restful import Resource, request

from amundsen_common.models.search import UpdateDocumentRequestSchema
from search_service.proxy import get_proxy_client
from search_service.proxy.es_search_proxy import RESOURCE_STR_MAPPING, Resource as AmundsenResource

LOGGER = logging.getLogger(__name__)


class DocumentAPI(Resource):

    def __init__(self) -> None:
        self.proxy = get_proxy_client()
        self.request = UpdateDocumentRequestSchema().loads(json.dumps(request.get_json()))

    def post(self):
        LOGGER.info(self.request)
        try:
            self.proxy.update_document_field(document_id=self.request.resource_key,
                                       resource_type=RESOURCE_STR_MAPPING.get(self.request.resource_type),
                                       field=self.request.field,
                                       value=self.request.value,
                                       delete=False)
        except Exception as e:
            err_msg = f'Exception encountered while processing search request {e}'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self):
        pass