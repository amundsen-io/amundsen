# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    List, Dict, Union,
)

import attr
from marshmallow3_annotations.ext.attrs import AttrsSchema

from search_service.models.resources import BaseResource


@attr.s(auto_attribs=True, kw_only=True)
class ResourceResults:
    total_results: int = attr.ib()
    results: List[BaseResource] = attr.ib(factory=list)


class ResourceResultsSchema(AttrsSchema):
    class Meta:
        target = ResourceResults
        register_as_scheme = True

@attr.s(auto_attribs=True, kw_only=True)
class SearchResult:
    page_index: int = attr.ib()
    results_per_page: int = attr.ib()
    search_results: Dict[str, ResourceResults] = attr.ib(factory=dict)


class SearchResultSchema(AttrsSchema):
    class Meta:
        target = SearchResult
        register_as_scheme = True
