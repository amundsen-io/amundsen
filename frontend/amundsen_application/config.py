import os
from typing import Dict, Set  # noqa: F401


class Config:
    LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d (%(process)d:' \
                 + '%(threadName)s) - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    LOG_LEVEL = 'INFO'
    COLUMN_STAT_ORDER = None  # type: Dict[str, int]

    UNEDITABLE_SCHEMAS = set()  # type: Set[str]

    # Number of popular tables to be displayed on the index/search page
    POPULAR_TABLE_COUNT = 4  # type: int


class LocalConfig(Config):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'DEBUG'

    # If installing locally directly from the github source
    # modify these ports if necessary to point to you local search and metadata services
    SEARCH_PORT = '5001'
    METADATA_PORT = '5002'

    # If installing using the Docker bootstrap, this should be modified to the docker host ip.
    LOCAL_HOST = '0.0.0.0'

    SEARCHSERVICE_REQUEST_CLIENT = None
    SEARCHSERVICE_REQUEST_HEADERS = None
    SEARCHSERVICE_BASE = os.environ.get('SEARCHSERVICE_BASE',
                                        'http://{LOCAL_HOST}:{PORT}'.format(
                                            LOCAL_HOST=LOCAL_HOST,
                                            PORT=SEARCH_PORT)
                                        )

    METADATASERVICE_REQUEST_CLIENT = None
    METADATASERVICE_REQUEST_HEADERS = None
    METADATASERVICE_BASE = os.environ.get('METADATASERVICE_BASE',
                                          'http://{LOCAL_HOST}:{PORT}'.format(
                                              LOCAL_HOST=LOCAL_HOST,
                                              PORT=METADATA_PORT)
                                          )

    # If specified, will be used to generate headers for service-to-service communication
    # Please note that if specified, this will ignore following config properties:
    # 1. METADATASERVICE_REQUEST_HEADERS
    # 2. SEARCHSERVICE_REQUEST_HEADERS
    REQUEST_HEADERS_METHOD = None

    AUTH_USER_METHOD = None
    GET_PROFILE_URL = None

    MAIL_CLIENT = None
