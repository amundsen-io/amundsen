from typing import Dict, Set  # noqa: F401


class Config:
    LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d (%(process)d:' \
                 + '%(threadName)s) - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    LOG_LEVEL = 'INFO'
    COLUMN_STAT_ORDER = None  # type: Dict[str, int]

    UNEDITABLE_SCHEMAS = set()  # type: Set[str]


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
    SEARCHSERVICE_ENDPOINT = 'http://{LOCAL_HOST}:{PORT}/search'.format(LOCAL_HOST=LOCAL_HOST, PORT=SEARCH_PORT)
    SEARCHSERVICE_REQUEST_HEADERS = None

    METADATASERVICE_REQUEST_CLIENT = None
    METADATASERVICE_POPULAR_TABLES_ENDPOINT = \
        'http://{LOCAL_HOST}:{PORT}/popular_tables'.format(LOCAL_HOST=LOCAL_HOST, PORT=METADATA_PORT)
    METADATASERVICE_LAST_INDEXED_ENDPOINT = \
        'http://{LOCAL_HOST}:{PORT}/latest_updated_ts'.format(LOCAL_HOST=LOCAL_HOST, PORT=METADATA_PORT)
    METADATASERVICE_TABLE_ENDPOINT = \
        'http://{LOCAL_HOST}:{PORT}/table'.format(LOCAL_HOST=LOCAL_HOST, PORT=METADATA_PORT)
    METADATASERVICE_TAGS_ENDPOINT = \
        'http://{LOCAL_HOST}:{PORT}/tags'.format(LOCAL_HOST=LOCAL_HOST, PORT=METADATA_PORT)
    METADATASERVICE_REQUEST_HEADERS = None

    CURRENT_USER_METHOD = None
    GET_PROFILE_URL = None

    MAIL_CLIENT = None
