# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from pyhocon import ConfigTree  # noqa: F401
from typing import Any  # noqa: F401

from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_utils import ModeDashboardUtils
from databuilder.rest_api.mode_analytics.mode_paginated_rest_api_query import ModePaginatedRestApiQuery
from databuilder.rest_api.rest_api_query import RestApiQuery  # noqa: F401

LOGGER = logging.getLogger(__name__)


class ModeDashboardUsageExtractor(Extractor):
    """
    A Extractor that extracts Mode dashboard's accumulated view count
    """

    def init(self, conf):
        # type: (ConfigTree) -> None

        self._conf = conf

        restapi_query = self._build_restapi_query()
        self._extractor = ModeDashboardUtils.create_mode_rest_api_extractor(restapi_query=restapi_query,
                                                                            conf=self._conf)

    def extract(self):
        # type: () -> Any

        return self._extractor.extract()

    def get_scope(self):
        # type: () -> str

        return 'extractor.mode_dashboard_usage'

    def _build_restapi_query(self):
        """
        Build REST API Query. To get Mode Dashboard usage, it needs to call two APIs (spaces API and reports
        API) joining together.
        :return: A RestApiQuery that provides Mode Dashboard metadata
        """
        # type: () -> RestApiQuery

        # https://mode.com/developer/api-reference/analytics/reports/#listReportsInSpace
        reports_url_template = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'

        spaces_query = ModeDashboardUtils.get_spaces_query_api(conf=self._conf)
        params = ModeDashboardUtils.get_auth_params(conf=self._conf)

        # Reports
        # JSONPATH expression. it goes into array which is located in _embedded.reports and then extracts token,
        # and view_count
        json_path = '_embedded.reports[*].[token,view_count]'
        field_names = ['dashboard_id', 'accumulated_view_count']
        reports_query = ModePaginatedRestApiQuery(query_to_join=spaces_query, url=reports_url_template, params=params,
                                                  json_path=json_path, field_names=field_names, skip_no_result=True)
        return reports_query
