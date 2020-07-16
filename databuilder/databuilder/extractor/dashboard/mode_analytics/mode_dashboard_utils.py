# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from pyhocon import ConfigTree, ConfigFactory  # noqa: F401
from requests.auth import HTTPBasicAuth

from databuilder import Scoped
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_constants import ORGANIZATION, MODE_ACCESS_TOKEN, \
    MODE_PASSWORD_TOKEN
from databuilder.extractor.restapi.rest_api_extractor import RestAPIExtractor, REST_API_QUERY, STATIC_RECORD_DICT
from databuilder.rest_api.base_rest_api_query import BaseRestApiQuery  # noqa: F401
from databuilder.rest_api.base_rest_api_query import RestApiQuerySeed
from databuilder.rest_api.rest_api_query import RestApiQuery  # noqa: F401


class ModeDashboardUtils(object):

    @staticmethod
    def get_spaces_query_api(conf,  # type: ConfigTree
                             ):
        """
        Provides RestApiQuerySeed where it will provides iterator of dictionaries as records where dictionary keys are
         organization, dashboard_group_id, dashboard_group and dashboard_group_description
        :param conf:
        :return:
        """
        # type: (...) -> BaseRestApiQuery

        # https://mode.com/developer/api-reference/management/spaces/#listSpaces
        spaces_url_template = 'https://app.mode.com/api/{organization}/spaces?filter=all'

        # Seed query record for next query api to join with
        seed_record = [{'organization': conf.get_string(ORGANIZATION)}]
        seed_query = RestApiQuerySeed(seed_record=seed_record)

        # Spaces
        params = {'auth': HTTPBasicAuth(conf.get_string(MODE_ACCESS_TOKEN),
                                        conf.get_string(MODE_PASSWORD_TOKEN))}

        json_path = '_embedded.spaces[*].[token,name,description]'
        field_names = ['dashboard_group_id', 'dashboard_group', 'dashboard_group_description']
        spaces_query = RestApiQuery(query_to_join=seed_query, url=spaces_url_template, params=params,
                                    json_path=json_path, field_names=field_names)

        return spaces_query

    @staticmethod
    def get_auth_params(conf,  # type: ConfigTree
                        ):
        params = {'auth': HTTPBasicAuth(conf.get_string(MODE_ACCESS_TOKEN),
                                        conf.get_string(MODE_PASSWORD_TOKEN)
                                        )
                  }
        return params

    @staticmethod
    def create_mode_rest_api_extractor(restapi_query,  # type: BaseRestApiQuery
                                       conf,  # type: ConfigTree
                                       ):
        """
        Creates RestAPIExtractor. Note that RestAPIExtractor is already initialized
        :param restapi_query:
        :param conf:
        :return: RestAPIExtractor. Note that RestAPIExtractor is already initialized
        """
        extractor = RestAPIExtractor()
        rest_api_extractor_conf = \
            Scoped.get_scoped_conf(conf, extractor.get_scope())\
                  .with_fallback(conf)\
                  .with_fallback(ConfigFactory.from_dict({REST_API_QUERY: restapi_query,
                                                          STATIC_RECORD_DICT: {'product': 'mode'}
                                                          }
                                                         )
                                 )

        extractor.init(conf=rest_api_extractor_conf)
        return extractor
