from http import HTTPStatus
from typing import Any, Dict, Iterable  # noqa: F401

from flask_restful import Resource, reqparse
from flasgger import swag_from

from search_service.models.table import SearchTableResultSchema
from search_service.proxy import get_proxy_client


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

            return SearchTableResultSchema().dump(results).data, HTTPStatus.OK

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR


class SearchTableFilterAPI(Resource):
    """
    Search Table API using search filtering

    This API should be generic enough to support every search filter use case.
    TODO: Deprecate the SearchTableFieldAPI for this more flexible API
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('index', required=False, default=TABLE_INDEX, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('query_term', required=False, type=str)
        self.parser.add_argument('search_request', type=dict)

        super(SearchTableFilterAPI, self).__init__()

    @swag_from('swagger_doc/table/search_table_filter.yml')
    def post(self) -> Iterable[Any]:
        """
        Fetch search results based on the page_index, query_term, and
        search_request dictionary posted in the request JSON.
        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.parser.parse_args(strict=True)
        page_index = args.get('page_index')  # type: int

        search_request = args.get('search_request')  # type: Dict
        if search_request is None:
            msg = 'The search request payload is not available in the request'
            return {'message': msg}, HTTPStatus.BAD_REQUEST

        query_term = args.get('query_term')  # type: str
        if ':' in query_term:
            msg = 'The query term contains an invalid character'
            return {'message': msg}, HTTPStatus.BAD_REQUEST

        try:
            results = self.proxy.fetch_table_search_results_with_filter(
                search_request=search_request,
                query_term=query_term,
                page_index=page_index,
                index=args['index']
            )
            return SearchTableResultSchema().dump(results).data, HTTPStatus.OK
        except RuntimeError:
            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
