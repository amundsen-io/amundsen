# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0import json


import logging
from .roundtrip_gremlin_proxy import RoundtripGremlinProxy
from metadata_service.proxy.janus_graph_proxy import JanusGraphGremlinProxy

LOGGER = logging.getLogger(__name__)


class RoundtripJanusGraphProxy(JanusGraphGremlinProxy, RoundtripGremlinProxy):
    pass
