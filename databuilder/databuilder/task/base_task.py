# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc

from pyhocon import ConfigTree  # noqa: F401

from databuilder import Scoped


class Task(Scoped):
    """
    A Abstract task that can run an abstract task
    """
    @abc.abstractmethod
    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    @abc.abstractmethod
    def run(self):
        # type: () -> None
        """
        Runs a task
        :return:
        """
        pass

    def get_scope(self):
        # type: () -> str
        return 'task'
