import logging

from pyhocon import ConfigTree, ConfigFactory  # noqa: F401
from requests.auth import HTTPBasicAuth
from typing import Any  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.restapi.rest_api_extractor import RestAPIExtractor, REST_API_QUERY, MODEL_CLASS, \
    STATIC_RECORD_DICT
from databuilder.rest_api.base_rest_api_query import RestApiQuerySeed
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
        self._extractor = RestAPIExtractor()
        rest_api_extractor_conf = Scoped.get_scoped_conf(conf, self._extractor.get_scope()).with_fallback(
            ConfigFactory.from_dict(
                {
                    REST_API_QUERY: restapi_query,
                    MODEL_CLASS: 'databuilder.models.dashboard_metadata.DashboardMetadata',
                    STATIC_RECORD_DICT: {'product': 'mode'}
                }
            )
        )

        self._extractor.init(conf=rest_api_extractor_conf)

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

        spaces_url_template = 'https://app.mode.com/api/{organization}/spaces?filter=all'
        reports_url_template = 'https://app.mode.com/api/{organization}/spaces/{dashboard_group_id}/reports'

        # Seed query record for next query api to join with
        seed_record = [{'organization': self._conf.get_string(ORGANIZATION)}]
        seed_query = RestApiQuerySeed(seed_record=seed_record)

        params = {'auth': HTTPBasicAuth(self._conf.get_string(MODE_ACCESS_TOKEN),
                                        self._conf.get_string(MODE_PASSWORD_TOKEN))}

        # Spaces
        # JSONPATH expression. it goes into array which is located in _embedded.spaces and then extracts token, name,
        # and description
        json_path = '_embedded.spaces[*].[token,name,description]'
        field_names = ['dashboard_group_id', 'dashboard_group', 'dashboard_group_description']
        spaces_query = RestApiQuery(query_to_join=seed_query, url=spaces_url_template, params=params,
                                    json_path=json_path, field_names=field_names)

        # Reports
        # JSONPATH expression. it goes into array which is located in _embedded.reports and then extracts token, name,
        # and description
        json_path = '_embedded.reports[*].[token,name,description]'
        field_names = ['dashboard_id', 'dashboard_name', 'description']
        reports_query = RestApiQuery(query_to_join=spaces_query, url=reports_url_template, params=params,
                                     json_path=json_path, field_names=field_names, skip_no_result=True)
        return reports_query
