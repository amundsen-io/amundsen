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
from databuilder.transformer.template_variable_substitution_transformer import (
    FIELD_NAME, TEMPLATE, TemplateVariableSubstitutionTransformer,
)

LOGGER = logging.getLogger(__name__)


class ModeDashboardChartsExtractor(Extractor):
    """
    A Extractor that extracts Dashboard charts

    """

    def init(self, conf: ConfigTree) -> None:
        self._conf = conf

        restapi_query = self._build_restapi_query()
        self._extractor = ModeDashboardUtils.create_mode_rest_api_extractor(
            restapi_query=restapi_query,
            conf=self._conf
        )

        # Constructing URL using resource path via TemplateVariableSubstitutionTransformer
        transformers: List[Transformer] = []
        chart_url_transformer = TemplateVariableSubstitutionTransformer()
        chart_url_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, chart_url_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict({FIELD_NAME: 'chart_url',
                                         TEMPLATE: 'https://app.mode.com{chart_url}'})))

        transformers.append(chart_url_transformer)

        dict_to_model_transformer = DictToModel()
        dict_to_model_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, dict_to_model_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict(
                    {MODEL_CLASS: 'databuilder.models.dashboard.dashboard_chart.DashboardChart'})))
        transformers.append(dict_to_model_transformer)

        self._transformer = ChainedTransformer(transformers=transformers)

    def extract(self) -> Any:
        record = self._extractor.extract()
        if not record:
            return None

        return self._transformer.transform(record=record)

    def get_scope(self) -> str:
        return 'extractor.mode_dashboard_chart'

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
        report_url_template = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'
        json_path = '(_embedded.reports[*].token)'
        field_names = ['dashboard_id']
        reports_query = ModePaginatedRestApiQuery(query_to_join=spaces_query, url=report_url_template, params=params,
                                                  json_path=json_path, field_names=field_names, skip_no_result=True)

        queries_url_template = 'https://app.mode.com/api/{organization}/reports/{dashboard_id}/queries'
        json_path = '_embedded.queries[*].[token,name]'
        field_names = ['query_id', 'query_name']
        query_names_query = RestApiQuery(query_to_join=reports_query, url=queries_url_template, params=params,
                                         json_path=json_path, field_names=field_names, skip_no_result=True)

        charts_url_template = 'https://app.mode.com/api/{organization}/reports/{dashboard_id}/queries/{query_id}/charts'
        json_path = '(_embedded.charts[*].token) | (_embedded.charts[*]._links.report_viz_web.href)'
        field_names = ['chart_id', 'chart_url']
        chart_names_query = RestApiQuery(query_to_join=query_names_query, url=charts_url_template, params=params,
                                         json_path=json_path, field_names=field_names, skip_no_result=True,
                                         json_path_contains_or=True)

        return chart_names_query
