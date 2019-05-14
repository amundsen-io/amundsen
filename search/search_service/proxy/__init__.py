from threading import Lock

from flask import current_app

from search_service import config
from search_service.proxy.base import BaseProxy
from werkzeug.utils import import_string

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
            host = current_app.config[config.PROXY_ENDPOINT]
            user = current_app.config[config.PROXY_USER]
            password = current_app.config[config.PROXY_PASSWORD]

            client = import_string(current_app.config[config.PROXY_CLIENT])
            _proxy_client = client(host=host, index=None, user=user, password=password)

    return _proxy_client
