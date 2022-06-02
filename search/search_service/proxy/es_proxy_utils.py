# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from enum import Enum
from typing import (
    Any, Dict, List,
)

from amundsen_common.models.search import SearchResponse
from elasticsearch_dsl.response import Response
from elasticsearch_dsl.response.hit import Hit
from elasticsearch_dsl.utils import AttrDict, AttrList


class Resource(Enum):
    TABLE = 0
    DASHBOARD = 1
    FEATURE = 2
    USER = 3


RESOURCE_STR_MAPPING = {
    "table": Resource.TABLE,
    "dashboard": Resource.DASHBOARD,
    "feature": Resource.FEATURE,
    "user": Resource.USER,
}


def get_index_for_resource(resource_type: Resource) -> str:
    resource_str = resource_type.name.lower()
    return f"{resource_str}_search_index"


class SearchHit():
    # custom wrapper for elasticsearch_dsl Hit
    def __init__(self, hit: Hit, fields_mapping: Dict):
        self.hit = hit
        self.fields_mapping = fields_mapping

    def _convert_attr_value_to_native(self, attr_value: Any) -> Any:
        if type(attr_value) is AttrDict:
            return attr_value.to_dict()
        elif type(attr_value) is AttrList:
            return list(attr_value)
        return attr_value

    def to_search_result(self) -> Dict:
        result = {}
        for field, mapped_field in self.fields_mapping.items():
            field_value = None
            # get field name instead of subfield
            mapped_field = mapped_field.split('.')[0]

            if field != mapped_field and hasattr(self.hit, mapped_field):
                # if the field name doesn't already match get mapped one
                field_value = getattr(self.hit, mapped_field)
            elif hasattr(self.hit, field):
                field_value = getattr(self.hit, field)

            result[field] = self._convert_attr_value_to_native(field_value)
        result["search_score"] = self.hit.meta.score
        return result

    def get_highlights(self) -> Dict:
        highlights = {}
        try:
            for highlighted_field, highlighted_value in self.hit.meta.highlight.to_dict().items():
                parent_field_name = highlighted_field.split('.')[0]
                highlights[parent_field_name] = highlighted_value
            return highlights

        except AttributeError:
            # response doesn't have highlights
            return highlights


def format_resource_response(response: Response, fields_mapping: Dict) -> Dict:
    results = []
    for hit in response.hits:
        search_hit = SearchHit(hit=hit, fields_mapping=fields_mapping)
        results.append({
            **search_hit.to_search_result(),
            'highlight': search_hit.get_highlights()
        })
    return {
        "results": results,
        "total_results": response.hits.total.value,
    }


def create_search_response(page_index: int,  # noqa: C901
                           results_per_page: int,
                           responses: List[Response],
                           resource_types: List[Resource],
                           resource_to_field_mapping: Dict) -> SearchResponse:
    results_per_resource = {}
    # responses are returned in the order in which the searches appear in msearch request
    for resource, response in zip(resource_types, responses):
        msg = ''
        status_code = 200
        if response.success():
            msg = 'Success'
            results_per_resource[resource.name.lower()] = \
                format_resource_response(response=response,
                                         fields_mapping=resource_to_field_mapping[resource])
        else:
            msg = f'Query response for {resource} returned an error: {response.to_dict()}'
            status_code = 500
            logging.error(msg)

    return SearchResponse(msg=msg,
                          page_index=page_index,
                          results_per_page=results_per_page,
                          results=results_per_resource,
                          status_code=status_code)
