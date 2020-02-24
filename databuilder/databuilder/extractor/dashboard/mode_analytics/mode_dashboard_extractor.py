import logging

from pyhocon import ConfigTree, ConfigFactory  # noqa: F401
from typing import Any  # noqa: F401

from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_utils import ModeDashboardUtils
from databuilder.extractor.restapi.rest_api_extractor import MODEL_CLASS
from databuilder.rest_api.rest_api_query import RestApiQuery

# CONFIG KEYS
ORGANIZATION = 'organization'
MODE_ACCESS_TOKEN = 'mode_user_token'
MODE_PASSWORD_TOKEN = 'mode_password_token'

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
        self._extractor = ModeDashboardUtils.create_mode_rest_api_extractor(
            restapi_query=restapi_query,
            conf=self._conf.with_fallback(
                ConfigFactory.from_dict(
                    {MODEL_CLASS: 'databuilder.models.dashboard_metadata.DashboardMetadata', }
                )
            )
        )

    def extract(self):
        # type: () -> Any

        return self._extractor.extract()

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
        json_path = '_embedded.reports[*].[token,name,description]'
        field_names = ['dashboard_id', 'dashboard_name', 'description']
        reports_query = RestApiQuery(query_to_join=spaces_query, url=reports_url_template, params=params,
                                     json_path=json_path, field_names=field_names, skip_no_result=True)
        return reports_query
