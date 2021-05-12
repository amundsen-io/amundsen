# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any

from pyhocon import ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_utils import ModeDashboardUtils
from databuilder.rest_api.mode_analytics.mode_paginated_rest_api_query import ModePaginatedRestApiQuery
from databuilder.rest_api.rest_api_failure_handlers import HttpFailureSkipOnStatus
from databuilder.rest_api.rest_api_query import RestApiQuery

LOGGER = logging.getLogger(__name__)


class ModeDashboardUsageExtractor(Extractor):
    """
    A Extractor that extracts Mode dashboard's accumulated view count
    """

    def init(self, conf: ConfigTree) -> None:
        self._conf = conf

        restapi_query = self._build_restapi_query()
        self._extractor = ModeDashboardUtils.create_mode_rest_api_extractor(restapi_query=restapi_query,
                                                                            conf=self._conf)

    def extract(self) -> Any:
        return self._extractor.extract()

    def get_scope(self) -> str:
        return 'extractor.mode_dashboard_usage'

    def _build_restapi_query(self) -> RestApiQuery:
        """
        Build REST API Query. To get Mode Dashboard usage, it needs to call two APIs (spaces API and reports
        API) joining together.
        :return: A RestApiQuery that provides Mode Dashboard metadata
        """

        # TODO: revise this extractor once Mode team provides total_views_count in reports discovery api
        # https://mode.com/developer/discovery-api/analytics/reports/
        # Once we can fully switch to Mode discovery api,
        # the performance of this extractor will be dramatically increased.

        # https://mode.com/developer/api-reference/analytics/reports/#listReportsInSpace
        reports_url_template = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'

        spaces_query = ModeDashboardUtils.get_spaces_query_api(conf=self._conf)
        params = ModeDashboardUtils.get_auth_params(conf=self._conf)

        # Reports
        # JSONPATH expression. it goes into array which is located in _embedded.reports and then extracts token,
        # and view_count
        json_path = '_embedded.reports[*].[token,view_count]'
        field_names = ['dashboard_id', 'accumulated_view_count']

        # the spaces_query is authenticated with a bearer token,
        # which returns spaces that may be beyond access of the user calling Mode main api.
        # When this happens, 404 will be returned and hence should be skipped.
        failure_handler = HttpFailureSkipOnStatus(status_codes_to_skip={404})
        reports_query = ModePaginatedRestApiQuery(query_to_join=spaces_query, url=reports_url_template, params=params,
                                                  json_path=json_path, field_names=field_names, skip_no_result=True,
                                                  can_skip_failure=failure_handler.can_skip_failure)
        return reports_query
