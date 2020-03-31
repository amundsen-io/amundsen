from http import HTTPStatus
from typing import Iterable, Any

from flasgger import swag_from
from flask_restful import Resource, fields, marshal_with, reqparse

from search_service.proxy import get_proxy_client


user_fields = {
    "name": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "team_name": fields.String,
    "email": fields.String,
    "manager_email": fields.String,
    "github_username": fields.String,
    "is_active": fields.Boolean,
    "employee_type": fields.String,
    "role_name": fields.String
}

search_user_results = {
    "total_results": fields.Integer,
    "results": fields.Nested(user_fields, default=[])
}

USER_INDEX = 'user_search_index'


class SearchUserAPI(Resource):
    """
    Search Table API
    """
    USER_INDEX = 'user_search_index'

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=True, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=SearchUserAPI.USER_INDEX, type=str)

        super(SearchUserAPI, self).__init__()

    @marshal_with(search_user_results)
    @swag_from('swagger_doc/user.yml')
    def get(self) -> Iterable[Any]:
        """
        Fetch search results based on query_term.
        :return: list of search results. List can be empty if query
        doesn't match any result
        """
        args = self.parser.parse_args(strict=True)

        try:

            results = self.proxy.fetch_user_search_results(
                query_term=args['query_term'],
                page_index=args['page_index'],
                index=args.get('index')
            )

            return results, HTTPStatus.OK

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
