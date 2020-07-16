# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from pyhocon import ConfigTree, ConfigFactory  # noqa: F401
from typing import Any  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_utils import ModeDashboardUtils
from databuilder.rest_api.mode_analytics.mode_paginated_rest_api_query import ModePaginatedRestApiQuery
from databuilder.rest_api.rest_api_query import RestApiQuery  # noqa: F401
from databuilder.transformer.base_transformer import ChainedTransformer
from databuilder.transformer.dict_to_model import DictToModel, MODEL_CLASS
from databuilder.transformer.template_variable_substitution_transformer import \
    TemplateVariableSubstitutionTransformer, TEMPLATE, FIELD_NAME as VAR_FIELD_NAME
from databuilder.transformer.timestamp_string_to_epoch import TimestampStringToEpoch, FIELD_NAME

LOGGER = logging.getLogger(__name__)


class ModeDashboardExtractor(Extractor):
    """
    A Extractor that extracts core metadata on Mode dashboard. https://app.mode.com/
    It extracts list of reports that consists of:
        Dashboard group name (Space name)
        Dashboard group id (Space token)
        Dashboard group description (Space description)
        Dashboard name (Report name)
        Dashboard id (Report token)
        Dashboard description (Report description)

    Other information such as report run, owner, chart name, query name is in separate extractor.
    """

    def init(self, conf):
        # type: (ConfigTree) -> None

        self._conf = conf

        restapi_query = self._build_restapi_query()
        self._extractor = ModeDashboardUtils.create_mode_rest_api_extractor(restapi_query=restapi_query,
                                                                            conf=self._conf)

        # Payload from RestApiQuery has timestamp which is ISO8601. Here we are using TimestampStringToEpoch to
        # transform into epoch and then using DictToModel to convert Dictionary to Model
        transformers = []
        timestamp_str_to_epoch_transformer = TimestampStringToEpoch()
        timestamp_str_to_epoch_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, timestamp_str_to_epoch_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict({FIELD_NAME: 'created_timestamp', })))

        transformers.append(timestamp_str_to_epoch_transformer)

        dashboard_group_url_transformer = TemplateVariableSubstitutionTransformer()
        dashboard_group_url_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, dashboard_group_url_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict({VAR_FIELD_NAME: 'dashboard_group_url',
                                         TEMPLATE: 'https://app.mode.com/{organization}/spaces/{dashboard_group_id}'})))

        transformers.append(dashboard_group_url_transformer)

        dashboard_url_transformer = TemplateVariableSubstitutionTransformer()
        dashboard_url_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, dashboard_url_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict({VAR_FIELD_NAME: 'dashboard_url',
                                         TEMPLATE: 'https://app.mode.com/{organization}/reports/{dashboard_id}'})))
        transformers.append(dashboard_url_transformer)

        dict_to_model_transformer = DictToModel()
        dict_to_model_transformer.init(
            conf=Scoped.get_scoped_conf(self._conf, dict_to_model_transformer.get_scope()).with_fallback(
                ConfigFactory.from_dict(
                    {MODEL_CLASS: 'databuilder.models.dashboard.dashboard_metadata.DashboardMetadata'})))
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

        return 'extractor.mode_dashboard'

    def _build_restapi_query(self):
        """
        Build REST API Query. To get Mode Dashboard metadata, it needs to call two APIs (spaces API and reports
        API) joining together.
        :return: A RestApiQuery that provides Mode Dashboard metadata
        """
        # type: () -> RestApiQuery

        # https://mode.com/developer/api-reference/analytics/reports/#listReportsInSpace
        reports_url_template = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'

        spaces_query = ModeDashboardUtils.get_spaces_query_api(conf=self._conf)
        params = ModeDashboardUtils.get_auth_params(conf=self._conf)

        # Reports
        # JSONPATH expression. it goes into array which is located in _embedded.reports and then extracts token, name,
        # and description
        json_path = '_embedded.reports[*].[token,name,description,created_at]'
        field_names = ['dashboard_id', 'dashboard_name', 'description', 'created_timestamp']
        reports_query = ModePaginatedRestApiQuery(query_to_join=spaces_query, url=reports_url_template, params=params,
                                                  json_path=json_path, field_names=field_names, skip_no_result=True)
        return reports_query
