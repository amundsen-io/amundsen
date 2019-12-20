import os

ELASTICSEARCH_INDEX_KEY = 'ELASTICSEARCH_INDEX'
SEARCH_PAGE_SIZE_KEY = 'SEARCH_PAGE_SIZE'
STATS_FEATURE_KEY = 'STATS'

PROXY_ENDPOINT = 'PROXY_ENDPOINT'
PROXY_USER = 'PROXY_USER'
PROXY_PASSWORD = 'PROXY_PASSWORD'
PROXY_CLIENT = 'PROXY_CLIENT'
PROXY_CLIENT_KEY = 'PROXY_CLIENT_KEY'
PROXY_CLIENTS = {
    'ELASTICSEARCH': 'search_service.proxy.elasticsearch.ElasticsearchProxy',
    'ATLAS': 'search_service.proxy.atlas.AtlasProxy'
}


class Config:
    LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d (%(process)d:'\
                 '%(threadName)s) - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    LOG_LEVEL = 'INFO'

    # Path to the logging configuration file to be used by `fileConfig()` method
    # https://docs.python.org/3.7/library/logging.config.html#logging.config.fileConfig
    # LOG_CONFIG_FILE = 'search_service/logging.conf'
    LOG_CONFIG_FILE = None

    # Used to differentiate tables with other entities in Atlas. For more details:
    # https://github.com/lyft/amundsenmetadatalibrary/blob/master/docs/proxy/atlas_proxy.md
    ATLAS_TABLE_ENTITY = 'Table'

    # The relationalAttribute name of Atlas Entity that identifies the database entity.
    ATLAS_DB_ATTRIBUTE = 'db'

    # Display name of Atlas Entities that we use for amundsen project.
    # Atlas uses qualifiedName as indexed attribute. but also supports 'name' attribute.
    ATLAS_NAME_ATTRIBUTE = 'qualifiedName'

    # Config used by ElastichSearch
    ELASTICSEARCH_INDEX = 'table_search_index'

    SWAGGER_ENABLED = False


class LocalConfig(Config):
    DEBUG = False
    TESTING = False
    STATS = False
    LOCAL_HOST = '0.0.0.0'
    PROXY_PORT = '9200'
    PROXY_ENDPOINT = os.environ.get('PROXY_ENDPOINT',
                                    'http://{LOCAL_HOST}:{PORT}'.format(
                                        LOCAL_HOST=LOCAL_HOST,
                                        PORT=PROXY_PORT)
                                    )
    PROXY_CLIENT = PROXY_CLIENTS[os.environ.get('PROXY_CLIENT', 'ELASTICSEARCH')]
    PROXY_CLIENT_KEY = os.environ.get('PROXY_CLIENT_KEY')
    PROXY_USER = os.environ.get('CREDENTIALS_PROXY_USER', 'elastic')
    PROXY_PASSWORD = os.environ.get('CREDENTIALS_PROXY_PASSWORD', 'elastic')

    SWAGGER_ENABLED = True
    SWAGGER_TEMPLATE_PATH = os.path.join('api', 'swagger_doc', 'template.yml')
    SWAGGER = {
        'openapi': '3.0.2',
        'title': 'Search Service',
        'uiversion': 3
    }
