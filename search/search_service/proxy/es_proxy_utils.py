# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from enum import Enum
from typing import Dict, List

from amundsen_common.models.search import SearchResponse
from elasticsearch_dsl.response import Response
from elasticsearch_dsl.utils import AttrDict, AttrList
from werkzeug.exceptions import InternalServerError


class Resource(Enum):
    TABLE = 0
    DASHBOARD = 1
    FEATURE = 2
    USER = 3


RESOURCE_STR_MAPPING = {
    'table': Resource.TABLE,
    'dashboard': Resource.DASHBOARD,
    'feature': Resource.FEATURE,
    'user': Resource.USER,
}


def get_index_for_resource(resource_type: Resource) -> str:
    resource_str = resource_type.name.lower()
    return f"{resource_str}_search_index"


def format_search_response(page_index: int,  # noqa: C901
                           results_per_page: int,
                           responses: List[Response],
                           resource_types: List[Resource],
                           resource_mapping: Dict) -> SearchResponse:
    resource_types_str = [r.name.lower() for r in resource_types]
    no_results_for_resource = {
        "results": [],
        "total_results": 0
    }
    results_per_resource = {resource: no_results_for_resource for resource in resource_types_str}

    for r in responses:
        if r.success():
            if len(r.hits.hits) > 0:
                resource_type = r.hits.hits[0]._source['resource_type']
                fields = resource_mapping[Resource[resource_type.upper()]]
                results = []
                for search_result in r.hits.hits:
                    # mapping gives all the fields in the response
                    result = {}
                    highlights_per_field = {}
                    for f in fields.keys():
                        # remove "keyword" from mapping value
                        field = fields[f].split('.')[0]
                        try:
                            result_for_field = search_result._source[field]
                            # AttrList and AttrDict are not json serializable
                            if type(result_for_field) is AttrList:
                                result_for_field = list(result_for_field)
                            elif type(result_for_field) is AttrDict:
                                result_for_field = result_for_field.to_dict()
                            result[f] = result_for_field
                        except KeyError:
                            logging.debug(f'Field: {field} missing in search response.')
                            pass
                    # add highlighting results if they exist for a hit
                    try:
                        for hf in search_result.highlight.to_dict().keys():
                            field = hf.split('.')[0]
                            field_highlight = search_result.highlight[hf]
                            if type(field_highlight) is AttrList:
                                field_highlight = list(field_highlight)
                            elif type(field_highlight) is AttrDict:
                                field_highlight = field_highlight.to_dict()
                            highlights_per_field[field] = field_highlight

                        result["highlight"] = highlights_per_field
                    except AttributeError:
                        # no highlights
                        pass

                    result["search_score"] = search_result._score
                    results.append(result)
                # replace empty results with actual results
                results_per_resource[resource_type] = {
                    "results": results,
                    "total_results": r.hits.total.value
                }

        else:
            raise InternalServerError(f"Request to Elasticsearch failed: {r.failures}")

    return SearchResponse(msg="Success",
                          page_index=page_index,
                          results_per_page=results_per_page,
                          results=results_per_resource,
                          status_code=200)
