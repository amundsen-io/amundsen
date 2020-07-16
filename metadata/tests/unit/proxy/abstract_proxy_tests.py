# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from abc import abstractmethod, ABC
from typing import Any, Callable, Generic, Type, TypeVar, no_type_check

from metadata_service.proxy.base_proxy import BaseProxy

__all__ = ['abstract_proxy_test_class']

T = TypeVar('T', bound=BaseProxy)


class AbstractProxyTest(ABC, Generic[T], unittest.TestCase):
    """
    Proxy integration testing

    use abstract_proxy_test_class() to get the class, e.g.

    class YourProxyTest(abstract_proxy_test_class(), unittest.TestCase):
        def get_proxy(self) -> YourProxy:
            return self.your_proxy
    ...
    """

    @abstractmethod
    def setUp(self) -> None:
        """
        this is for implementing classes (if they need it)
        """
        pass

    @abstractmethod
    def tearDown(self) -> None:
        """
        this is for implementing classes (if they need it)
        """
        pass

    @abstractmethod
    def get_proxy(self) -> T:
        pass


@no_type_check
def class_getter_closure() -> Callable[[], Type[AbstractProxyTest]]:  # noqa: F821
    the_class: Type[AbstractProxyTest[Any]] = AbstractProxyTest  # noqa: F821

    def abstract_proxy_test_class() -> Type[AbstractProxyTest]:  # noqa: F821
        return the_class
    return abstract_proxy_test_class


abstract_proxy_test_class: Callable[[], Type[AbstractProxyTest]] = class_getter_closure()
del AbstractProxyTest
del class_getter_closure
