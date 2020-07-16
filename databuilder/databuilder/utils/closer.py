# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import atexit

from typing import Callable, List  # noqa: F401


class Closer(object):
    """
    A Closer class that is responsible for collecting closeable callable,
    and close it in group. Registered closeable callable will be guaranteed
    to be called where only last occurred failure will be propagated back.

    Order of closing registered closeable callable will be LIFO
    as closeable instance can have dependency each other.
    """

    def __init__(self):
        # type: () -> None
        self._stack = []  # type: List
        atexit.register(self.close)

    def register(self, close_callable):
        # type: (Callable) -> None
        """
        Register closeable callable.
        :param close_callable:
        :return: None
        """
        if not callable(close_callable):
            raise RuntimeError('Only callable can be registered: {}'.format(
                close_callable))

        self._stack.append(close_callable)

    def close(self):
        # type: () -> None
        """
        Execute all closeable callable in LIFO order.
        All registered callable will be guaranteed to be executed. If there
        are multiple failures, only the last one will be propagated.
        :return:
        """
        if not self._stack:
            return

        last_exception = None
        while len(self._stack):
            try:
                close_callable = self._stack.pop()
                close_callable()
            except Exception as e:
                last_exception = e

        if last_exception:
            raise last_exception
