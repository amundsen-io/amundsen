# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from pyhocon import ConfigTree, ConfigFactory  # noqa: F401
from typing import Any  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_utils import ModeDashboardUtils
from databuilder.rest_api.mode_analytics.mode_paginated_rest_api_query import ModePaginatedRestApiQuery
from databuilder.rest_api.rest_api_query import RestApiQuery
from databuilder.transformer.base_transformer import ChainedTransformer
from databuilder.transformer.dict_to_model import DictToModel, MODEL_CLASS
from databuilder.transformer.regex_str_replace_transformer import RegexStrReplaceTransformer, \
    REGEX_REPLACE_TUPLE_LIST, ATTRIBUTE_NAME
from databuilder.transformer.template_variable_substitution_transformer import \
    TemplateVariableSubstitutionTransformer, TEMPLATE, FIELD_NAME

LOGGER = logging.getLogger(__name__)


class ModeDashboardQueriesExtractor(Extractor):
    """
    A Extractor that extracts Query information

    """

    def init(self, conf):
        # type: (ConfigTree) -> None
        self._conf = conf

        restapi_query = self._build_restapi_query()
        self._extractor = ModeDashboardUtils.create_mode_rest_api_extractor(
            restapi_query=restapi_query,
            conf=self._conf
        )

        # Constructing URL using several ID via TemplateVariableSubstitutionTransformer
        transformers = []
        variable_substitution_transformer = TemplateVariableSubstitutionTransformer()
        variable_substitution_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf,
                                        variable_substitution_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict({FIELD_NAME: 'url',
                                         TEMPLATE: 'https://app.mode.com/{organization}'
                                                   '/reports/{dashboard_id}/queries/{query_id}'})))

        transformers.append(variable_substitution_transformer)

        # Escape backslash as it breaks Cypher statement.
        replace_transformer = RegexStrReplaceTransformer()
        replace_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, replace_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict(
                    {REGEX_REPLACE_TUPLE_LIST: [('\\', '\\\\')], ATTRIBUTE_NAME: 'query_text'})))
        transformers.append(replace_transformer)

        dict_to_model_transformer = DictToModel()
        dict_to_model_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, dict_to_model_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict(
                    {MODEL_CLASS: 'databuilder.models.dashboard.dashboard_query.DashboardQuery'})))
        transformers.append(dict_to_model_transformer)

        self._transformer = ChainedTransformer(transformers=transformers)

    def extract(self):
        # type: () -> Any

        record = self._extractor.extract()
        if not record:
            return None

        return self._transformer.transform(record=record)

    def get_scope(self):
        # type: () -> str
        return 'extractor.mode_dashboard_query'

    def _build_restapi_query(self):
        """
        Build REST API Query. To get Mode Dashboard last execution, it needs to call three APIs (spaces API, reports
        API, and queries API) joining together.
        :return: A RestApiQuery that provides Mode Dashboard execution (run)
        """
        # type: () -> RestApiQuery

        spaces_query = ModeDashboardUtils.get_spaces_query_api(conf=self._conf)
        params = ModeDashboardUtils.get_auth_params(conf=self._conf)

        # Reports
        # https://mode.com/developer/api-reference/analytics/reports/#listReportsInSpace
        url = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'
        json_path = '(_embedded.reports[*].token)'
        field_names = ['dashboard_id']
        reports_query = ModePaginatedRestApiQuery(query_to_join=spaces_query, url=url, params=params,
                                                  json_path=json_path, field_names=field_names, skip_no_result=True)

        queries_url_template = 'https://app.mode.com/api/{organization}/reports/{dashboard_id}/queries'
        json_path = '_embedded.queries[*].[token,name,raw_query]'
        field_names = ['query_id', 'query_name', 'query_text']
        query_names_query = RestApiQuery(query_to_join=reports_query, url=queries_url_template, params=params,
                                         json_path=json_path, field_names=field_names, skip_no_result=True)

        return query_names_query
