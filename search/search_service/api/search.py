# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Iterable, List  # noqa: F401
import logging
import json

from flasgger import swag_from
from flask_restful import Resource, request

from amundsen_common.models.search import SearchRequestSchema

from search_service.proxy.es_search_proxy import ElasticsearchProxy, Resource as AMDResource, RESOURCE_STR_MAPPING

LOGGER = logging.getLogger(__name__)


class SearchAPI(Resource):
    """
    Search API handles search requests for filtered and unfiltered search
    """

    def __init__(self) -> None:
        self.search_proxy = ElasticsearchProxy()

    @swag_from('swagger_doc/search/search.yml')
    def post(self) -> Iterable[Any]:
        """
        Fetch search results
        :return: json payload of schema
        """

        request_data = SearchRequestSchema().loads(json.dumps(request.get_json()))
        
        resources: List[AMDResource] = []
        for r in request.get_json().get('resource_types'):
            resource: AMDResource = RESOURCE_STR_MAPPING.get(r)    
            if resource:
                resources.append(resource)
            else:
                err_msg = f'Search for invalid resource "{r}" requested'
                return {'message': err_msg}, HTTPStatus.BAD_REQUEST

        try:
            from pprint import pprint
            pprint(request_data.filters)
            search_results = self.search_proxy.search(query_term=request_data.query_term,
                                                      page_index=request_data.page_index,
                                                      results_per_page=request_data.results_per_page,
                                                      resource_types=resources,
                                                      filters=request_data.filters) 
            return self.results_schema().dump(search_results), HTTPStatus.OK

        except RuntimeError as e:
            err_msg = f'Exception encountered while processing search request {e}'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
