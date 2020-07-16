# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from metadata_service.proxy.aws4authwebsocket.transport import (Aws4AuthWebsocketTransport,
                                                                WebsocketClientTransport)
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from .gremlin_proxy import AbstractGremlinProxy, _parse_gremlin_server_error
import gremlin_python.driver.protocol
from overrides import overrides
from typing import Any, Mapping, Optional, Union


def _is_neptune_concurrent_modification_exception(exception: Exception) -> bool:
    if not isinstance(exception, gremlin_python.driver.protocol.GremlinServerError):
        return False
    return _parse_gremlin_server_error(exception).get('code') == 'ConcurrentModificationException'


class NeptuneGremlinProxy(AbstractGremlinProxy):
    """
    A proxy to a Neptune using the Gremlin protocol.

    See also https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html
    See also https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-sessions.html
    """

    def __init__(self, *, host: str, port: Optional[int] = None, user: str = None,
                 password: Optional[Union[str, Mapping[str, str]]] = None,
                 driver_remote_connection_options: Mapping[str, Any] = {},
                 aws4auth_options: Mapping[str, Any] = {}, websocket_options: Mapping[str, Any] = {}) -> None:
        driver_remote_connection_options = dict(driver_remote_connection_options)
        # as others, we repurpose host a url
        driver_remote_connection_options.update(url=host)
        # port should be part of that url
        if port is not None:
            raise NotImplementedError(f'port is not allowed! port={port}')

        # always g for Neptune
        driver_remote_connection_options.update(traversal_source='g')

        # for IAM auth, we need the triplet
        if isinstance(password, Mapping):
            if user or 'aws_access_key_id' not in password or 'aws_secret_access_key' not in password or \
               'service_region' not in password:
                raise NotImplementedError(f'to use authentication, pass a Mapping with aws_access_key_id, '
                                          f'aws_secret_access_key, service_region!')

            aws_access_key_id = password['aws_access_key_id']
            aws_secret_access_key = password['aws_secret_access_key']
            service_region = password['service_region']

            def factory() -> Aws4AuthWebsocketTransport:
                return Aws4AuthWebsocketTransport(aws_access_key_id=aws_access_key_id,
                                                  aws_secret_access_key=aws_secret_access_key,
                                                  service_region=service_region,
                                                  extra_aws4auth_options=aws4auth_options or {},
                                                  extra_websocket_options=websocket_options or {})
            driver_remote_connection_options.update(transport_factory=factory)
        elif password is not None:
            raise NotImplementedError(f'to use authentication, pass a Mapping with aws_access_key_id, '
                                      f'aws_secret_access_key, service_region!')
        else:
            raise NotImplementedError(f'to use authentication, pass a Mapping with aws_access_key_id, '
                                      f'aws_secret_access_key, service_region!')

            # we could use the default Transport, but then we'd have to take different options, which feels clumsier.
            def factory() -> WebsocketClientTransport:
                return WebsocketClientTransport(extra_websocket_options=websocket_options or {})
            driver_remote_connection_options.update(transport_factory=factory)

        super().__init__(key_property_name='key',
                         remote_connection=DriverRemoteConnection(**driver_remote_connection_options))

    @classmethod
    @overrides
    def _is_retryable_exception(cls, *, method_name: str, exception: Exception) -> bool:
        # any method
        return _is_neptune_concurrent_modification_exception(exception)
