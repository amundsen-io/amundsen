import logging

from http import HTTPStatus
from typing import Tuple, Any

from flask_restful import Resource, reqparse
from search_service.proxy import get_proxy_client
from search_service.models.table import TableSchema
from search_service.api.table import TABLE_INDEX

LOGGER = logging.getLogger(__name__)


class DocumentTableAPI(Resource):

    def __init__(self) -> None:
        self.proxy = get_proxy_client()
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument('index', required=False, default=TABLE_INDEX, type=str)
        super(DocumentTableAPI, self).__init__()

    def post(self) -> Tuple[Any, int]:
        """
        Uses the Elasticsearch bulk API to load data from JSON. Uses Elasticsearch
        index actions to create or update documents by id

        :param data: list of data objects to be indexed in Elasticsearch
        :return: name of new index
        """
        self.parser.add_argument('data', required=True)
        args = self.parser.parse_args()

        try:
            data = TableSchema(many=True, unknown='EXCLUDE').loads(args.get('data'))
            results = self.proxy.create_document(data=data, index=args.get('index'))
            return results, HTTPStatus.OK
        except RuntimeError as e:
            err_msg = 'Exception encountered while updating documents '
            LOGGER.error(err_msg + str(e))
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR

    def put(self) -> Tuple[Any, int]:
        """
        Uses the Elasticsearch bulk API to update existing documents by id. Will
        ignore ids it doesn't recognize (ids are defined in models)

        :param data: list of data objects to be indexed in Elasticsearch
        :return: name of index
        """
        self.parser.add_argument('data', required=True)
        args = self.parser.parse_args()

        try:
            data = TableSchema(many=True, unknown='EXCLUDE').loads(args.get('data'))
            results = self.proxy.update_document(data=data, index=args.get('index'))
            return results, HTTPStatus.OK
        except RuntimeError as e:
            err_msg = 'Exception encountered while updating documents '
            LOGGER.error(err_msg + str(e))
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self, *, document_id: str) -> Tuple[Any, int]:
        """
        Uses the Elasticsearch bulk API to delete existing documents by id

        :param document_id: document id for document to be deleted
        :return:
        """
        args = self.parser.parse_args()

        try:
            self.proxy.delete_document(data=[document_id], index=args.get('index'))
            return {}, HTTPStatus.OK
        except RuntimeError as e:
            err_msg = 'Exception encountered while deleting document '
            LOGGER.error(err_msg + str(e))
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
