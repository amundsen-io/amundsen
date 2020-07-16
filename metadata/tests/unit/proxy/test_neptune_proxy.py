# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import gremlin_python.driver.protocol
import json
from typing import Any, Mapping
import unittest

from metadata_service.proxy.neptune_proxy import NeptuneGremlinProxy

from .abstract_gremlin_proxy_tests import abstract_gremlin_proxy_test_class


class NeptuneGremlinProxyTest(
        abstract_gremlin_proxy_test_class(), unittest.TestCase):  # type: ignore
    def _create_gremlin_proxy(self, config: Mapping[str, Any]) -> NeptuneGremlinProxy:
        # Don't use PROXY_HOST, PROXY_PORT, PROXY_PASSWORD.  They might not be neptune
        return NeptuneGremlinProxy(host=config['NEPTUNE_URL'], password=config['NEPTUNE_CREDENTIALS'])

    def test_is_retryable(self) -> None:
        exception = gremlin_python.driver.protocol.GremlinServerError(dict(
            code=408, attributes=(), message=json.dumps(dict(code='ConcurrentModificationException'))))
        self.assertTrue(NeptuneGremlinProxy._is_retryable_exception(method_name=None, exception=exception))
        exception = gremlin_python.driver.protocol.GremlinServerError(dict(
            code=408, attributes=(), message=json.dumps(dict(code='InternalError'))))
        self.assertFalse(NeptuneGremlinProxy._is_retryable_exception(method_name=None, exception=exception))
        exception = RuntimeError()
        self.assertFalse(NeptuneGremlinProxy._is_retryable_exception(method_name=None, exception=exception))


# this may not work locally, depending on setup. Remove the line below
# to run the abstract gremlin tests with neptune
del NeptuneGremlinProxyTest
