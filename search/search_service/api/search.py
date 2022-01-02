# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
from http import HTTPStatus
from typing import (  # noqa: F401
    Any, Iterable, List,
)

from amundsen_common.models.search import SearchRequestSchema, SearchResponseSchema
from flasgger import swag_from
from flask_restful import Resource, request

from search_service.proxy import get_proxy_client
from search_service.proxy.es_proxy_utils import RESOURCE_STR_MAPPING, Resource as AmundsenResource


class SearchAPI(Resource):
    """
    Search API handles search requests for filtered and unfiltered search
    """

    def __init__(self) -> None:
        self.search_proxy = get_proxy_client()

    @swag_from('swagger_doc/search/search.yml')
    def post(self) -> Iterable[Any]:
        """
        Fetch search results
        :return: json payload of schema
        """

        request_data = SearchRequestSchema().loads(json.dumps(request.get_json()))

        resources: List[AmundsenResource] = []
        for r in request.get_json().get('resource_types'):
            resource = RESOURCE_STR_MAPPING.get(r)
            if resource:
                resources.append(resource)
            else:
                err_msg = f'Search for invalid resource "{r}" requested'
                return {'message': err_msg}, HTTPStatus.BAD_REQUEST

        try:
            search_results = self.search_proxy.search(query_term=request_data.query_term,
                                                      page_index=request_data.page_index,
                                                      results_per_page=request_data.results_per_page,
                                                      resource_types=resources,
                                                      filters=request_data.filters)
            return SearchResponseSchema().dump(search_results), HTTPStatus.OK

        except RuntimeError as e:
            err_msg = f'Exception encountered while processing search request {e}'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
