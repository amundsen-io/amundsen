# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Set, List

import attr

from marshmallow_annotations.ext.attrs import AttrsSchema
from amundsen_common.models.dashboard import DashboardSummary, DashboardSummarySchema

from search_service.models.base import Base


@attr.s(auto_attribs=True, kw_only=True)
class Dashboard(Base,
                DashboardSummary):
    """
    This represents the part of a dashboard stored in the search proxy
    """

    def get_id(self) -> str:
        # uses the table key as the document id in ES
        return self.name

    @classmethod
    def get_attrs(cls) -> Set:
        return {
            'uri',
            'cluster',
            'group_name',
            'group_url',
            'product',
            'name',
            'url',
            'description',
            'last_successful_run_timestamp'
        }

    @staticmethod
    def get_type() -> str:
        return 'dashboard'


class DashboardSchema(DashboardSummarySchema):
    class Meta:
        target = Dashboard
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchDashboardResult:
    total_results: int = attr.ib()
    results: List[Dashboard] = attr.ib(factory=list)


class SearchDashboardResultSchema(AttrsSchema):
    class Meta:
        target = SearchDashboardResult
        register_as_scheme = True
