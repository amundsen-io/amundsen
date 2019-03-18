import os

# PROXY configuration keys
PROXY_HOST = 'PROXY_HOST'
PROXY_PORT = 'PROXY_PORT'
PROXY_USER = 'PROXY_USER'
PROXY_PASSWORD = 'PROXY_PASSWORD'
PROXY_CLIENT = 'PROXY_CLIENT'


PROXY_CLIENTS = {
    'NEO4J': 'metadata_service.proxy.neo4j_proxy.Neo4jProxy'
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


class LocalConfig(Config):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    LOCAL_HOST = '0.0.0.0'
    NEO4J_ENDPOINT = 'bolt://{LOCAL_HOST}:7687'.format(LOCAL_HOST=LOCAL_HOST)

    PROXY_HOST = f'bolt://{LOCAL_HOST}'
    PROXY_PORT = 7687
    PROXY_CLIENT = PROXY_CLIENTS['NEO4J']
