from typing import Iterable, Any

from flask_restful import Resource, fields, marshal_with, reqparse

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
}

search_results = {
    "total_results": fields.Integer,
    "results": fields.Nested(table_fields, default=[])
}


class SearchAPI(Resource):
    """
    Search API
    """
    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=True, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)

        super(SearchAPI, self).__init__()

    @marshal_with(search_results)
    def get(self) -> Iterable[Any]:
        """
        Fetch search results based on query_term.
        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.parser.parse_args(strict=True)

        try:

            results = self.proxy.fetch_search_results(
                query_term=args['query_term'],
                page_index=args['page_index']
            )

            return results, 200

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, 500


class SearchFieldAPI(Resource):
    """
    Search API with explict field
    """
    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=False, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)

        super(SearchFieldAPI, self).__init__()

    @marshal_with(search_results)
    def get(self, *, field_name: str,
            field_value: str) -> Iterable[Any]:
        """
        Fetch search results based on query_term.

        :param field_name: which field we should search from(schema, tag, table)
        :param field_value: the value to search for the field
        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.parser.parse_args(strict=True)

        try:
            results = self.proxy.fetch_search_results_with_field(
                query_term=args.get('query_term'),
                field_name=field_name,
                field_value=field_value,
                page_index=args['page_index']
            )

            return results, 200

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, 500
