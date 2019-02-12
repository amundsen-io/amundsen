import os


NEO4J_ENDPOINT_KEY = 'NEO4J_ENDPOINT'
NEO4J_USER = 'NEO4J_USER'
NEO4J_PASSWORD = 'NEO4J_PASSWORD'

IS_STATSD_ON = 'IS_STATSD_ON'


class Config:
    LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d (%(process)d:'\
                 '%(threadName)s) - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    LOG_LEVEL = 'INFO'
    NEO4J_USER = os.environ.get('CREDENTIALS_NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.environ.get('CREDENTIALS_NEO4J_PASSWORD', '')

    IS_STATSD_ON = False


class LocalConfig(Config):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    LOCAL_HOST = '0.0.0.0'
    NEO4J_ENDPOINT = 'bolt://{LOCAL_HOST}:7687'.format(LOCAL_HOST=LOCAL_HOST)
