# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from pyhocon import ConfigTree, ConfigFactory  # noqa: F401
from typing import Any  # noqa: F401

from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_utils import ModeDashboardUtils
from databuilder.extractor.restapi.rest_api_extractor import MODEL_CLASS
from databuilder.rest_api.mode_analytics.mode_paginated_rest_api_query import ModePaginatedRestApiQuery
from databuilder.rest_api.rest_api_failure_handlers import HttpFailureSkipOnStatus
from databuilder.rest_api.rest_api_query import RestApiQuery

LOGGER = logging.getLogger(__name__)


class ModeDashboardOwnerExtractor(Extractor):
    """
    An Extractor that extracts Dashboard owner.

    """

    def init(self, conf):
        # type: (ConfigTree) -> None
        self._conf = conf

        restapi_query = self._build_restapi_query()
        self._extractor = ModeDashboardUtils.create_mode_rest_api_extractor(
            restapi_query=restapi_query,
            conf=self._conf.with_fallback(
                ConfigFactory.from_dict(
                    {MODEL_CLASS: 'databuilder.models.dashboard.dashboard_owner.DashboardOwner', }
                )
            )
        )

    def extract(self):
        # type: () -> Any

        return self._extractor.extract()

    def get_scope(self):
        # type: () -> str
        return 'extractor.mode_dashboard_owner'

    def _build_restapi_query(self):
        """
        Build REST API Query. To get Mode Dashboard owner, it needs to call three APIs (spaces API, reports
        API, and user API) joining together.
        :return: A RestApiQuery that provides Mode Dashboard owner
        """
        # type: () -> RestApiQuery

        # https://mode.com/developer/api-reference/analytics/reports/#listReportsInSpace
        report_url_template = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'

        # https://mode.com/developer/api-reference/management/users/
        creator_url_template = 'https://app.mode.com{creator_resource_path}'

        spaces_query = ModeDashboardUtils.get_spaces_query_api(conf=self._conf)
        params = ModeDashboardUtils.get_auth_params(conf=self._conf)

        # Reports
        json_path = '(_embedded.reports[*].token) | (_embedded.reports[*]._links.creator.href)'
        field_names = ['dashboard_id', 'creator_resource_path']
        creator_resource_path_query = ModePaginatedRestApiQuery(query_to_join=spaces_query, url=report_url_template,
                                                                params=params,
                                                                json_path=json_path, field_names=field_names,
                                                                skip_no_result=True,
                                                                json_path_contains_or=True)

        json_path = 'email'
        field_names = ['email']
        failure_handler = HttpFailureSkipOnStatus(status_codes_to_skip={404})
        owner_email_query = RestApiQuery(query_to_join=creator_resource_path_query, url=creator_url_template,
                                         params=params,
                                         json_path=json_path, field_names=field_names, skip_no_result=True,
                                         can_skip_failure=failure_handler.can_skip_failure)

        return owner_email_query
