# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional, Dict, Any

import attr

from marshmallow3_annotations.ext.attrs import AttrsSchema

@attr.s(auto_attribs=True, kw_only=True)
class Filter:
    name = str
    values = List[str]
    operation = str

class FilterSchema(AttrsSchema):
    class Meta:
        target = Filter
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchRequest:
    query_term = str,
    resource_types = List[str]
    page_index = int
    results_per_page = int
    filters = List[Filter]


class SearchRequestSchema(AttrsSchema):
    class Meta:
        target = SearchRequest
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchResponse:
    msg = str,
    page_index = int
    results_per_page = int
    results = Dict
    status_code = int


class SearchResponseSchema(AttrsSchema):
    class Meta:
        target = SearchResponse
        register_as_scheme = True
