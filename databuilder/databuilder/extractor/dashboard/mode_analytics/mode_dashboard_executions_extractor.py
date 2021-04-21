# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, List

from pyhocon import ConfigFactory, ConfigTree

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_utils import ModeDashboardUtils
from databuilder.rest_api.mode_analytics.mode_paginated_rest_api_query import ModePaginatedRestApiQuery
from databuilder.rest_api.rest_api_query import RestApiQuery
from databuilder.transformer.base_transformer import ChainedTransformer, Transformer
from databuilder.transformer.dict_to_model import MODEL_CLASS, DictToModel
from databuilder.transformer.timestamp_string_to_epoch import FIELD_NAME, TimestampStringToEpoch

LOGGER = logging.getLogger(__name__)


class ModeDashboardExecutionsExtractor(Extractor):
    """
    A Extractor that extracts run (execution) status and timestamp.

    """

    def init(self, conf: ConfigTree) -> None:
        self._conf = conf

        restapi_query = self._build_restapi_query()
        self._extractor = ModeDashboardUtils.create_mode_rest_api_extractor(
            restapi_query=restapi_query,
            conf=self._conf
        )

        # Payload from RestApiQuery has timestamp which is ISO8601. Here we are using TimestampStringToEpoch to
        # transform into epoch and then using DictToModel to convert Dictionary to Model
        transformers: List[Transformer] = []
        timestamp_str_to_epoch_transformer = TimestampStringToEpoch()
        timestamp_str_to_epoch_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, timestamp_str_to_epoch_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict({FIELD_NAME: 'execution_timestamp', })))

        transformers.append(timestamp_str_to_epoch_transformer)

        dict_to_model_transformer = DictToModel()
        dict_to_model_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, dict_to_model_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict(
                    {MODEL_CLASS: 'databuilder.models.dashboard.dashboard_execution.DashboardExecution'})))
        transformers.append(dict_to_model_transformer)

        self._transformer = ChainedTransformer(transformers=transformers)

    def extract(self) -> Any:
        record = self._extractor.extract()
        if not record:
            return None

        return self._transformer.transform(record=record)

    def get_scope(self) -> str:
        return 'extractor.mode_dashboard_execution'

    def _build_restapi_query(self) -> RestApiQuery:
        """
        Build REST API Query. To get Mode Dashboard last execution, it needs to call three APIs (spaces API, reports
        API, and run API) joining together.
        :return: A RestApiQuery that provides Mode Dashboard execution (run)
        """

        spaces_query = ModeDashboardUtils.get_spaces_query_api(conf=self._conf)
        params = ModeDashboardUtils.get_auth_params(conf=self._conf)

        # Reports
        # https://mode.com/developer/api-reference/analytics/reports/#listReportsInSpace
        url = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'
        json_path = '(_embedded.reports[*].token) | (_embedded.reports[*]._links.last_run.href)'
        field_names = ['dashboard_id', 'last_run_resource_path']
        last_run_resource_path_query = ModePaginatedRestApiQuery(query_to_join=spaces_query, url=url, params=params,
                                                                 json_path=json_path, field_names=field_names,
                                                                 skip_no_result=True,
                                                                 json_path_contains_or=True)

        # https://mode.com/developer/api-reference/analytics/report-runs/#getReportRun
        url = 'https://app.mode.com{last_run_resource_path}'
        json_path = '[state,completed_at]'
        field_names = ['execution_state', 'execution_timestamp']
        last_run_state_query = RestApiQuery(query_to_join=last_run_resource_path_query, url=url, params=params,
                                            json_path=json_path, field_names=field_names, skip_no_result=True)

        return last_run_state_query
