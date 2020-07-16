# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional, Set

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema

from .base import Base
from search_service.models.tag import Tag


@attr.s(auto_attribs=True, kw_only=True)
class Table(Base):
    """
    This represents the part of a table stored in the search proxy
    """
    database: str
    cluster: str
    schema: str
    name: str
    key: str
    display_name: Optional[str] = None
    tags: List[Tag]
    badges: List[Tag]
    description: Optional[str] = None
    last_updated_timestamp: int
    # The following properties are lightly-transformed properties from the normal table object:
    column_names: List[str]
    column_descriptions: List[str] = []
    programmatic_descriptions: List[str] = []
    # The following are search-only properties:
    total_usage: int = 0
    schema_description: Optional[str] = attr.ib(default=None)

    def get_id(self) -> str:
        # uses the table key as the document id in ES
        return self.key

    @classmethod
    def get_attrs(cls) -> Set:
        return {
            'name',
            'key',
            'description',
            'cluster',
            'database',
            'schema',
            'column_names',
            'tags',
            'badges',
            'last_updated_timestamp',
            'display_name',
            'programmatic_descriptions',
            'schema_description',
        }

    @staticmethod
    def get_type() -> str:
        return 'table'


class TableSchema(AttrsSchema):
    class Meta:
        target = Table
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchTableResult:
    total_results: int = attr.ib()
    results: List[Table] = attr.ib(factory=list)


class SearchTableResultSchema(AttrsSchema):
    class Meta:
        target = SearchTableResult
        register_as_scheme = True
