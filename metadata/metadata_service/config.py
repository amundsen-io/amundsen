import os

# PROXY configuration keys
PROXY_HOST = 'PROXY_HOST'
PROXY_PORT = 'PROXY_PORT'
PROXY_USER = 'PROXY_USER'
PROXY_PASSWORD = 'PROXY_PASSWORD'
PROXY_CLIENT = 'PROXY_CLIENT'


PROXY_CLIENTS = {
    'NEO4J': 'metadata_service.proxy.neo4j_proxy.Neo4jProxy',
    'ATLAS': 'metadata_service.proxy.atlas_proxy.AtlasProxy'
}

IS_STATSD_ON = 'IS_STATSD_ON'


class Config:
    LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d (%(process)d:'\
                 '%(threadName)s) - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    LOG_LEVEL = 'INFO'

    PROXY_USER = os.environ.get('CREDENTIALS_PROXY_USER', 'neo4j')
    PROXY_PASSWORD = os.environ.get('CREDENTIALS_PROXY_PASSWORD', 'test')

    IS_STATSD_ON = False

    # Used to differentiate tables with other entities in Atlas. For more details:
    # https://github.com/lyft/amundsenmetadatalibrary/blob/master/docs/proxy/atlas_proxy.md
    ATLAS_TABLE_ENTITY = 'Table'

    # The relationalAttribute name of Atlas Entity that identifies the database entity.
    ATLAS_DB_ATTRIBUTE = 'db'

    # Display name of Atlas Entities that we use for amundsen project.
    # Atlas uses qualifiedName as indexed attribute. but also supports 'name' attribute.
    ATLAS_NAME_ATTRIBUTE = 'qualifiedName'


class LocalConfig(Config):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    LOCAL_HOST = '0.0.0.0'

    PROXY_HOST = os.environ.get('PROXY_HOST', f'bolt://{LOCAL_HOST}')
    PROXY_PORT = os.environ.get('PROXY_PORT', 7687)
    PROXY_CLIENT = PROXY_CLIENTS[os.environ.get('PROXY_CLIENT', 'NEO4J')]
