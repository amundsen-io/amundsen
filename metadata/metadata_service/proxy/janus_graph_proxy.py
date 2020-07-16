# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from metadata_service.proxy.aws4authwebsocket.transport import WebsocketClientTransport
from .gremlin_proxy import AbstractGremlinProxy
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from typing import Any, Mapping, Optional


class JanusGraphGremlinProxy(AbstractGremlinProxy):
    """
    A proxy to a JanusGraph using the Gremlin protocol.

    """

    def __init__(self, *, host: str, port: Optional[int] = None, user: Optional[str] = None,
                 password: Optional[str] = None, traversal_source: 'str' = 'g',
                 driver_remote_connection_options: Mapping[str, Any] = {},
                 websocket_options: Mapping[str, Any] = {}) -> None:
        driver_remote_connection_options = dict(driver_remote_connection_options)

        # as others, we repurpose host a url
        driver_remote_connection_options.update(url=host)
        # port should be part of that url
        if port is not None:
            raise NotImplementedError(f'port is not allowed! port={port}')

        if user is not None:
            driver_remote_connection_options.update(username=user)
        if password is not None:
            driver_remote_connection_options.update(password=password)

        driver_remote_connection_options.update(traversal_source=traversal_source)

        # we could use the default Transport, but then we'd have to take different options, which feels clumsier.
        def factory() -> WebsocketClientTransport:
            return WebsocketClientTransport(extra_websocket_options=websocket_options or {})
        driver_remote_connection_options.update(transport_factory=factory)

        # use _key
        super().__init__(key_property_name='_key',
                         remote_connection=DriverRemoteConnection(**driver_remote_connection_options))
