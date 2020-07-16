# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc

from pyhocon import ConfigTree  # noqa: F401
from typing import Any  # noqa: F401

from databuilder import Scoped


class Extractor(Scoped):
    """
    An extractor extracts record
    """

    @abc.abstractmethod
    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    @abc.abstractmethod
    def extract(self):
        # type: () -> Any
        """
        :return: Provides a record or None if no more to extract
        """
        return None

    def get_scope(self):
        # type: () -> str
        return 'extractor'
