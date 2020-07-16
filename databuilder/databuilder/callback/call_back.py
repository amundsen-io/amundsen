# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
import logging
import six

from typing import List, Optional  # noqa: F401

LOGGER = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Callback(object):
    """
    A callback interface that expected to fire "on_success" if the operation is successful, else "on_failure" if
    operation failed.
    """

    @abc.abstractmethod
    def on_success(self):
        # type: () -> None
        """
        A call back method that will be called when operation is successful
        :return: None
        """
        pass

    @abc.abstractmethod
    def on_failure(self):
        # type: () -> None
        """
        A call back method that will be called when operation failed
        :return: None
        """
        pass


def notify_callbacks(callbacks, is_success):
    """
    A Utility method that notifies callback. If any callback fails it will still go through all the callbacks,
    and raise the last exception it experienced.

    :param callbacks:
    :param is_success:
    :return:
    """
    # type: (List[Callback], bool) -> None

    if not callbacks:
        LOGGER.info('No callbacks to notify')
        return

    LOGGER.info('Notifying callbacks')

    last_exception = None  # type: Optional[Exception]
    for callback in callbacks:
        try:
            if is_success:
                callback.on_success()
            else:
                callback.on_failure()
        except Exception as e:
            LOGGER.exception('Failed while notifying callback')
            last_exception = e

    if last_exception:
        raise last_exception
