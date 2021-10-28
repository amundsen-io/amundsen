# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import time
from typing import (
    List, Dict, Optional
)

import attr
from marshmallow3_annotations.ext.attrs import AttrsSchema

from search_service.models.tag import Tag


@attr.s(auto_attribs=True, kw_only=True)
class BaseResource():
    search_score: int
    id: str
    key: str
    name: str
    description: Optional[str] = None
    display_name: Optional[str] = None
    tags: Optional[List[Tag]] = None
    badges: Optional[List[Tag]] = None  # TODO update mapping to be badge
    last_updated_timestamp: int = int(time.time())

@attr.s(auto_attribs=True, kw_only=True)
class BaseResourceSchema(AttrsSchema):
    class Meta:
        target = BaseResource
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Table(BaseResource):
    """
    This represents the part of a table stored in the search proxy
    """
    database: str
    cluster: str
    schema: str
    # The following properties are lightly-transformed properties from the normal table object:
    column_names: Optional[List[str]] = None
    column_descriptions: Optional[List[str]] = None
    programmatic_descriptions: Optional[List[str]] = None
    # The following are search-only properties:
    total_usage: int = 0
    schema_description: Optional[str] = attr.ib(default=None)


class TableSchema(AttrsSchema):
    class Meta:
        target = Table
        register_as_scheme = True
