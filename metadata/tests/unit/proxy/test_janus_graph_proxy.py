# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Mapping
import unittest

from metadata_service.proxy.janus_graph_proxy import JanusGraphGremlinProxy

from .abstract_gremlin_proxy_tests import abstract_gremlin_proxy_test_class


class JanusGraphGremlinProxyTest(
        abstract_gremlin_proxy_test_class(), unittest.TestCase):  # type: ignore
    def _create_gremlin_proxy(self, config: Mapping[str, Any]) -> JanusGraphGremlinProxy:
        # Don't use PROXY_HOST, PROXY_PORT, PROXY_PASSWORD.  They might not be JanusGraph
        return JanusGraphGremlinProxy(host=config['JANUS_GRAPH_URL'])


# this may not work locally, depending on setup. Remove the line below
# to run the abstract gremlin tests with neptune
del JanusGraphGremlinProxyTest
