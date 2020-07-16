# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc

from pyhocon import ConfigTree  # noqa: F401

from databuilder import Scoped
from typing import Any  # noqa: F401


class Loader(Scoped):
    """
    A loader loads to the destination or to the staging area
    """
    @abc.abstractmethod
    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    @abc.abstractmethod
    def load(self, record):
        # type: (Any) -> None
        pass

    def get_scope(self):
        # type: () -> str
        return 'loader'
