# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from pyhocon import ConfigTree, ConfigFactory  # noqa: F401

from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_executions_extractor import \
    ModeDashboardExecutionsExtractor
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_utils import ModeDashboardUtils
from databuilder.extractor.restapi.rest_api_extractor import STATIC_RECORD_DICT
from databuilder.rest_api.mode_analytics.mode_paginated_rest_api_query import ModePaginatedRestApiQuery
from databuilder.rest_api.rest_api_query import RestApiQuery  # noqa: F401
from databuilder.transformer.dict_to_model import DictToModel, MODEL_CLASS
from databuilder.transformer.timestamp_string_to_epoch import TimestampStringToEpoch, FIELD_NAME

LOGGER = logging.getLogger(__name__)


class ModeDashboardLastModifiedTimestampExtractor(ModeDashboardExecutionsExtractor):
    """
    A Extractor that extracts Mode dashboard's last modified timestamp.

    """

    def __init__(self):
        super(ModeDashboardLastModifiedTimestampExtractor, self).__init__()

    def init(self, conf):
        # type: (ConfigTree) -> None

        conf = conf.with_fallback(
            ConfigFactory.from_dict({
                STATIC_RECORD_DICT: {'product': 'mode'},
                '{}.{}'.format(DictToModel().get_scope(), MODEL_CLASS):
                    'databuilder.models.dashboard.dashboard_last_modified.DashboardLastModifiedTimestamp',
                '{}.{}'.format(TimestampStringToEpoch().get_scope(), FIELD_NAME):
                    'last_modified_timestamp'
            })
        )
        super(ModeDashboardLastModifiedTimestampExtractor, self).init(conf)

    def get_scope(self):
        # type: () -> str
        return 'extractor.mode_dashboard_last_modified_timestamp_execution'

    def _build_restapi_query(self):
        """
        Build REST API Query. To get Mode Dashboard last modified timestamp, it needs to call two APIs (spaces API,
        and reports API) joining together.
        :return: A RestApiQuery that provides Mode Dashboard last successful execution (run)
        """
        # type: () -> RestApiQuery

        spaces_query = ModeDashboardUtils.get_spaces_query_api(conf=self._conf)
        params = ModeDashboardUtils.get_auth_params(conf=self._conf)

        # Reports
        # https://mode.com/developer/api-reference/analytics/reports/#listReportsInSpace
        url = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'
        json_path = '_embedded.reports[*].[token,edited_at]'
        field_names = ['dashboard_id', 'last_modified_timestamp']
        last_modified_query = ModePaginatedRestApiQuery(query_to_join=spaces_query, url=url, params=params,
                                                        json_path=json_path, field_names=field_names,
                                                        skip_no_result=True)

        return last_modified_query
