import os
import logging

from flask import Flask, Blueprint
from flask_restful import Api

from search_service.api.search import SearchAPI, SearchFieldAPI
from search_service.api.healthcheck import healthcheck


def create_app(*, config_module_class: str) -> Flask:
    """
    Creates app in function so that flask with flask extensions can be
    initialized with specific config. Here it defines the route of APIs
    so that it can be seen in one place where implementation is separated.

    Config is being fetched via module.class name where module.class name
    can be passed through environment variable.
    This is to make config fetched through runtime PYTHON_PATH so that
    Config class can be easily injected.
    More on: http://flask.pocoo.org/docs/1.0/config/

    :param config_module_class: name of the config
    :return: Flask
    """

    app = Flask(__name__)

    logging.info('Creating app with config name {}'
                 .format(config_module_class))
    config_module_class = \
        os.getenv('SEARCH_SVC_CONFIG_MODULE_CLASS') or config_module_class
    app.config.from_object(config_module_class)

    logging.basicConfig(format=app.config.get('LOG_FORMAT'), datefmt=app.config.get('LOG_DATE_FORMAT'))
    logging.getLogger().setLevel(app.config.get('LOG_LEVEL'))
    logging.info('Created app with config name {}'.format(config_module_class))

    api_bp = Blueprint('api', __name__)
    api_bp.add_url_rule('/healthcheck', 'healthcheck', healthcheck)
    api = Api(api_bp)
    api.add_resource(SearchAPI, '/search')
    api.add_resource(SearchFieldAPI,
                     '/search/field/<field_name>/field_val/<field_value>')

    app.register_blueprint(api_bp)

    return app
