# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Iterable  # noqa: F401

from flasgger import swag_from
from flask_restful import Resource, reqparse
from marshmallow3_annotations.ext.attrs import AttrsSchema

from search_service.models.results import SearchResultSchema
from search_service.proxy.es_search_proxy import ElasticsearchProxy


class SearchAPI(Resource):
    """
    Search API handles search requests for filtered and unfiltered search
    """

    def __init__(self) -> None:
        self.search_proxy = ElasticsearchProxy()  # TODO add new es search proxy when done
        self.results_schema = SearchResultSchema

        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument('query_term', required=True, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('results_per_page', required=False, default=10, type=int)
        self.parser.add_argument('resource_types', required=False, default=[], type=list)
        self.parser.add_argument('filters', required=False, default=[], type=dict)

    @swag_from('swagger_doc/search/search.yml')
    def post(self) -> Iterable[Any]:
        """
        Fetch search results
        :return: json payload of schema
        """
        args = self.parser.parse_args(strict=True)

        query_term = args.get('query_term')
        page_index = args.get('page_index')
        results_per_page = args.get('results_per_page')
        resource_types = args.get('resource_types')
        filters = args.get('filters')

        try:
            search_results = self.search_proxy.get_search_results()  # TODO get results from proxy
            # print("HERE")
            # print(search_results)
            return self.results_schema().dump(search_results), HTTPStatus.OK

        except RuntimeError as e:
            raise e
