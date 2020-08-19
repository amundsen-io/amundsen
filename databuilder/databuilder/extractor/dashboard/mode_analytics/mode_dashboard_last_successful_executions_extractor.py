# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from pyhocon import ConfigTree, ConfigFactory

from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_executions_extractor import \
    ModeDashboardExecutionsExtractor
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_utils import ModeDashboardUtils
from databuilder.extractor.restapi.rest_api_extractor import STATIC_RECORD_DICT
from databuilder.models.dashboard.dashboard_execution import DashboardExecution
from databuilder.rest_api.mode_analytics.mode_paginated_rest_api_query import ModePaginatedRestApiQuery
from databuilder.rest_api.rest_api_query import RestApiQuery

LOGGER = logging.getLogger(__name__)


class ModeDashboardLastSuccessfulExecutionExtractor(ModeDashboardExecutionsExtractor):
    """
    A Extractor that extracts Mode dashboard's last successful run (execution) timestamp.

    """

    def __init__(self) -> None:
        super(ModeDashboardLastSuccessfulExecutionExtractor, self).__init__()

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(
            ConfigFactory.from_dict({
                STATIC_RECORD_DICT: {'product': 'mode',
                                     'execution_state': 'succeeded',
                                     'execution_id': DashboardExecution.LAST_SUCCESSFUL_EXECUTION_ID}
            })
        )
        super(ModeDashboardLastSuccessfulExecutionExtractor, self).init(conf)

    def get_scope(self) -> str:
        return 'extractor.mode_dashboard_last_successful_execution'

    def _build_restapi_query(self) -> RestApiQuery:
        """
        Build REST API Query. To get Mode Dashboard last successful execution, it needs to call two APIs (spaces API,
        and reports API) joining together.
        :return: A RestApiQuery that provides Mode Dashboard last successful execution (run)
        """

        spaces_query = ModeDashboardUtils.get_spaces_query_api(conf=self._conf)
        params = ModeDashboardUtils.get_auth_params(conf=self._conf)

        # Reports
        # https://mode.com/developer/api-reference/analytics/reports/#listReportsInSpace
        url = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'
        json_path = '_embedded.reports[*].[token,last_successfully_run_at]'
        field_names = ['dashboard_id', 'execution_timestamp']
        last_successful_run_query = ModePaginatedRestApiQuery(query_to_join=spaces_query, url=url, params=params,
                                                              json_path=json_path, field_names=field_names,
                                                              skip_no_result=True)

        return last_successful_run_query
