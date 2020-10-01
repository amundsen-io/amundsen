# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Mapping
import unittest

from .abstract_gremlin_proxy_tests import abstract_gremlin_proxy_test_class
from .roundtrip_janusgraph_proxy import RoundtripJanusGraphProxy


class JanusGraphGremlinProxyTest(
        abstract_gremlin_proxy_test_class(), unittest.TestCase):  # type: ignore
    def _create_gremlin_proxy(self, config: Mapping[str, Any]) -> RoundtripJanusGraphProxy:
        # Don't use PROXY_HOST, PROXY_PORT, PROXY_PASSWORD.  They might not be JanusGraph
        return RoundtripJanusGraphProxy(host=config['JANUS_GRAPH_URL'])
