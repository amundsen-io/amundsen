# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import time
from typing import (
    List, Optional, Set,
)

import attr
from marshmallow3_annotations.ext.attrs import AttrsSchema

from search_service.models.base import Base


@attr.s(auto_attribs=True, kw_only=True)
class Report(Base):
    """
    This represents the part of a report stored in the search proxy
    """
    id: str
    key: str
    name: str
    source: Optional[str] = None
    workspace: Optional[str] = None
    description: Optional[str] = None
    webUrl: Optional[str] = None

    def get_id(self) -> str:
        return self.id

    def get_attrs_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def get_attrs(cls) -> Set:
        return {
            'id',
            'key',
            'name',
            'source',
            'workspace',
            'description',
            'webUrl'
        }

    @staticmethod
    def get_type() -> str:
        return 'report'


class ReportSchema(AttrsSchema):
    class Meta:
        target = Report
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchReportResult:
    total_results: int = attr.ib()
    results: List[Report] = attr.ib(factory=list)


class SearchReportResultSchema(AttrsSchema):
    class Meta:
        target = SearchReportResult
        register_as_scheme = True
