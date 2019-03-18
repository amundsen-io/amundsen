from http import HTTPStatus
from typing import Iterable, Union, Mapping

from flask_restful import Resource, fields, marshal

from metadata_service.proxy import get_proxy_client

popular_table_fields = {
    'database': fields.String,
    'cluster': fields.String,
    'schema': fields.String,
    'table_name': fields.String(attribute='name'),
    'table_description': fields.String(attribute='description'),  # Optional
}

popular_tables_fields = {
    'popular_tables': fields.List(fields.Nested(popular_table_fields))
}


class PopularTablesAPI(Resource):
    """
    PopularTables API
    """
    def __init__(self) -> None:
        self.client = get_proxy_client()

    def get(self) -> Iterable[Union[Mapping, int, None]]:
        popular_tables = self.client.get_popular_tables()
        return marshal({'popular_tables': popular_tables}, popular_tables_fields), HTTPStatus.OK
