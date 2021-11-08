# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Iterable, List  # noqa: F401
import logging


from flasgger import swag_from
from flask_restful import Resource, reqparse, request

from search_service.models.results import SearchResultSchema
from search_service.proxy.es_search_proxy import ElasticsearchProxy, Filter, Resource as AMDResource, RESOURCE_STR_MAPPING

LOGGER = logging.getLogger(__name__)


class SearchAPI(Resource):
    """
    Search API handles search requests for filtered and unfiltered search
    """

    def __init__(self) -> None:
        self.search_proxy = ElasticsearchProxy()
        self.results_schema = SearchResultSchema

        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument('query_term', required=True, default="", type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('results_per_page', required=False, default=10, type=int)
        self.parser.add_argument('resource_types', required=False, default=[], type=list, location='json')
        self.parser.add_argument('filters', required=False, default=[], type=dict)

    @swag_from('swagger_doc/search/search.yml')
    def post(self) -> Iterable[Any]:
        """
        Fetch search results
        :return: json payload of schema
        """

        args = self.parser.parse_args(strict=False)
        query_term = args.get('query_term')
        page_index = args.get('page_index')
        results_per_page = args.get('results_per_page')
        resource_types = args.get('resource_types')
        filters = args.get('filters')

        resources: List[AMDResource] = []
        for r in resource_types:
            resource: AMDResource = RESOURCE_STR_MAPPING.get(r)
            if resource:
                resources.append(resource)
            else:
                raise ValueError(f'Search requested for invalid resource {r}')
        
        filter_objs: List[Filter] = []
        for f in filters.keys():
            filter = Filter(name=f,
                            values=filters.get(f).get('values'),
                            operation=filters.get(f).get('operation'))
            filter_objs.append(filter)

        try:
            search_results = self.search_proxy.search(query_term=query_term,
                                                      page_index=page_index,
                                                      results_per_page=results_per_page,
                                                      resource_types=resources,
                                                      filters=filter_objs) 
            return self.results_schema().dump(search_results), HTTPStatus.OK

        except RuntimeError as e:
            raise e
