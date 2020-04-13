import logging
from http import HTTPStatus
from typing import Iterable, Any

from flask_restful import fields, Resource, marshal_with, reqparse  # noqa: I201
from flasgger import swag_from

from search_service.exception import NotFoundException
from search_service.proxy import get_proxy_client


DASHBOARD_INDEX = 'dashboard_search_index'

LOGGING = logging.getLogger(__name__)

# todo: Use common to produce this
dashboard_fields = {
    "uri": fields.String,
    "cluster": fields.String,
    "group_name": fields.String,
    "group_url": fields.String,
    "product": fields.String,
    "name": fields.String,
    "url": fields.String,
    "description": fields.String,
    "last_successful_run_timestamp": fields.Integer
}

search_dashboard_results = {
    "total_results": fields.Integer,
    "results": fields.Nested(dashboard_fields, default=[])
}


class SearchDashboardAPI(Resource):
    """
    Search Dashboard API
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=True, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=DASHBOARD_INDEX, type=str)

        super(SearchDashboardAPI, self).__init__()

    @marshal_with(search_dashboard_results)
    @swag_from('swagger_doc/dashboard/search_dashboard.yml')
    def get(self) -> Iterable[Any]:
        """
        Fetch dashboard search results based on query_term.

        :return: list of dashboard  results. List can be empty if query
        doesn't match any dashboards
        """
        args = self.parser.parse_args(strict=True)
        try:
            results = self.proxy.fetch_dashboard_search_results(
                query_term=args.get('query_term'),
                page_index=args['page_index'],
                index=args['index']
            )

            return results, HTTPStatus.OK

        except NotFoundException:
            return {'message': 'query_term does not exist'}, HTTPStatus.NOT_FOUND

        except Exception:

            err_msg = 'Exception encountered while processing search request'
            LOGGING.exception(err_msg)
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
