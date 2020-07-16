# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from abc import abstractmethod
from metadata_service import create_app
from metadata_service.proxy.gremlin_proxy import AbstractGremlinProxy
from typing import Any, Callable, Mapping, Type, TypeVar, no_type_check
import unittest

from flask import Flask

from .abstract_proxy_tests import abstract_proxy_test_class

V = TypeVar('V')


def make_retryable_callable(callable: Callable[[], V], retries: int = 1,
                            exception_factory: Callable[[], Exception] = RuntimeError) -> Callable[[], V]:
    def wrapped() -> V:
        nonlocal retries
        v: V = callable()
        if retries > 0:
            retries -= 1
            raise exception_factory()
        return v
    return wrapped


class AbstractGremlinProxyTest(abstract_proxy_test_class(), unittest.TestCase):  # type: ignore
    """
    Gremlin proxy integration testing
    """

    @classmethod
    @abstractmethod
    def _create_gremlin_proxy(cls, config: Mapping[str, Any]) -> AbstractGremlinProxy:
        pass

    def setUp(self) -> None:
        self.app: Flask = create_app(config_module_class='metadata_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config['PROXY_HOST']
        self.gremlin_proxy = self._create_gremlin_proxy(self.app.config)
        self.drop_everything()
        self.key_property_name = self.gremlin_proxy.key_property_name
        self.maxDiff = None

    def drop_everything(self) -> None:
        self.gremlin_proxy.g.V().drop().toList()

    def tearDown(self) -> None:
        pass

    def get_proxy(self) -> AbstractGremlinProxy:
        return self.gremlin_proxy


@no_type_check
def class_getter_closure() -> Callable[[], Type[AbstractGremlinProxyTest]]:  # noqa: F821
    the_class: Type[AbstractGremlinProxyTest[Any]] = AbstractGremlinProxyTest  # noqa: F821

    def abstract_gremlin_proxy_test_class() -> Type[AbstractGremlinProxyTest]:  # noqa: F821
        return the_class
    return abstract_gremlin_proxy_test_class


# so we don't try to test it directly
abstract_gremlin_proxy_test_class: Callable[[], Type[AbstractGremlinProxyTest]] = class_getter_closure()
del AbstractGremlinProxyTest
del class_getter_closure
