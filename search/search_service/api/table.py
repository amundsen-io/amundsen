from http import HTTPStatus
from typing import Iterable, Any

from flask_restful import Resource, fields, marshal_with, reqparse
from flasgger import swag_from


from search_service.proxy import get_proxy_client

table_fields = {
    "name": fields.String,
    "key": fields.String,
    # description can be empty, if no description is present in DB
    "description": fields.String,
    "cluster": fields.String,
    "database": fields.String,
    "schema_name": fields.String,
    "column_names": fields.List(fields.String),
    # tags can be empty list
    "tags": fields.List(fields.String),
    # last etl timestamp as epoch
    "last_updated_epoch": fields.Integer,
    "display_name": fields.String
}

search_table_results = {
    "total_results": fields.Integer,
    "results": fields.Nested(table_fields, default=[])
}

TABLE_INDEX = 'table_search_index'


class SearchTableAPI(Resource):
    """
    Search Table API
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=True, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=TABLE_INDEX, type=str)

        super(SearchTableAPI, self).__init__()

    @marshal_with(search_table_results)
    @swag_from('swagger_doc/table/search_table.yml')
    def get(self) -> Iterable[Any]:
        """
        Fetch search results based on query_term.
        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.parser.parse_args(strict=True)

        try:

            results = self.proxy.fetch_table_search_results(
                query_term=args.get('query_term'),
                page_index=args.get('page_index'),
                index=args.get('index')
            )

            return results, HTTPStatus.OK

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR


class SearchTableFieldAPI(Resource):
    """
    Search Table API with explict field
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=False, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=TABLE_INDEX, type=str)
        super(SearchTableFieldAPI, self).__init__()

    @marshal_with(search_table_results)
    @swag_from('swagger_doc/table/search_table_field.yml')
    def get(self, *, field_name: str, field_value: str) -> Iterable[Any]:
        """
        Fetch search results based on query_term.

        :param field_name: which field we should search from(schema, tag, table)
        :param field_value: the value to search for the field
        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.parser.parse_args(strict=True)

        try:
            results = self.proxy.fetch_table_search_results_with_field(
                query_term=args.get('query_term'),
                field_name=field_name,
                field_value=field_value,
                page_index=args.get('page_index'),
                index=args.get('index')
            )

            return results, HTTPStatus.OK

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
