# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, List, Optional, Dict

import attr

from marshmallow3_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class HighlightOptions:
    enable_highlight: bool = False


class HighlightOptionsSchema(AttrsSchema):
    class Meta:
        target = HighlightOptions
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Filter:
    name: str
    values: List[str]
    operation: str


class FilterSchema(AttrsSchema):
    class Meta:
        target = Filter
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchRequest:
    query_term: str
    resource_types: List[str] = []
    page_index: Optional[int] = 0
    results_per_page: Optional[int] = 10
    filters: List[Filter] = []
    # highlight options are defined per resource
    highlight_options: Optional[Dict[str, HighlightOptions]] = {}


class SearchRequestSchema(AttrsSchema):
    class Meta:
        target = SearchRequest
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchResponse:
    msg: str
    page_index: int
    results_per_page: int
    results: Dict[str, Any]
    status_code: int


class SearchResponseSchema(AttrsSchema):
    class Meta:
        target = SearchResponse
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class UpdateDocumentRequest:
    resource_key: str
    resource_type: str
    field: str
    value: Optional[str]
    operation: str  # can be add or overwrite


class UpdateDocumentRequestSchema(AttrsSchema):
    class Meta:
        target = UpdateDocumentRequest
        register_as_scheme = True
