from threading import Lock

from flask import current_app
from werkzeug.utils import import_string

from metadata_service import config
from metadata_service.proxy.base_proxy import BaseProxy

_proxy_client = None
_proxy_client_lock = Lock()


def get_proxy_client() -> BaseProxy:
    """
    Provides singleton proxy client based on the config
    :return: Proxy instance of any subclass of BaseProxy
    """
    global _proxy_client

    if _proxy_client:
        return _proxy_client

    with _proxy_client_lock:
        if _proxy_client:
            return _proxy_client
        else:
            # Gather all the configuration to create a Proxy Client
            host = current_app.config[config.PROXY_HOST]
            port = current_app.config[config.PROXY_PORT]
            user = current_app.config[config.PROXY_USER]
            password = current_app.config[config.PROXY_PASSWORD]

            client = import_string(current_app.config[config.PROXY_CLIENT])
            _proxy_client = client(host=host, port=port, user=user, password=password)

    return _proxy_client
