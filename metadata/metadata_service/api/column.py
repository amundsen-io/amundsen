from http import HTTPStatus
from typing import Iterable, Union

from flask_restful import Resource, reqparse

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client


class ColumnDescriptionAPI(Resource):
    """
    ColumnDescriptionAPI supports PUT and GET operations to upsert column description
    """
    def __init__(self) -> None:
        self.client = get_proxy_client()

        self.parser = reqparse.RequestParser()
        self.parser.add_argument('description', type=str, location='json')

        super(ColumnDescriptionAPI, self).__init__()

    def put(self,
            table_uri: str,
            column_name: str,
            description_val: str) -> Iterable[Union[dict, tuple, int, None]]:
        """
        Updates column description
        """
        try:
            self.client.put_column_description(table_uri=table_uri,
                                               column_name=column_name,
                                               description=description_val)

            return None, HTTPStatus.OK

        except NotFoundException:
            msg = 'table_uri {} with column {} does not exist'.format(table_uri, column_name)
            return {'message': msg}, HTTPStatus.NOT_FOUND

    def get(self, table_uri: str, column_name: str) -> Union[tuple, int, None]:
        """
        Gets column descriptions in Neo4j
        """
        try:
            description = self.client.get_column_description(table_uri=table_uri,
                                                             column_name=column_name)

            return {'description': description}, HTTPStatus.OK

        except NotFoundException:
            msg = 'table_uri {} with column {} does not exist'.format(table_uri, column_name)
            return {'message': msg}, HTTPStatus.NOT_FOUND

        except Exception:
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR
