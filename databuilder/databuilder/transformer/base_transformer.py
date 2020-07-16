# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc

from pyhocon import ConfigTree  # noqa: F401
from typing import Any, Iterable, Optional  # noqa: F401

from databuilder import Scoped


class Transformer(Scoped):
    """
    A transformer transforms a record
    """
    @abc.abstractmethod
    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    @abc.abstractmethod
    def transform(self, record):
        # type: (Any) -> Any
        pass


class NoopTransformer(Transformer):
    """
    A no-op transformer
    """

    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    def transform(self, record):
        # type: (Any) -> Any
        return record

    def get_scope(self):
        # type: () -> str
        pass


class ChainedTransformer(Transformer):
    """
    A chained transformer that iterates transformers and transforms a record
    """

    def __init__(self,
                 transformers,
                 is_init_transformers=False):
        # type: (Iterable[Transformer], Optional[bool]) -> None
        self.transformers = transformers
        self.is_init_transformers = is_init_transformers

    def init(self, conf):
        # type: (ConfigTree) -> None
        if self.is_init_transformers:
            for transformer in self.transformers:
                transformer.init(Scoped.get_scoped_conf(conf, transformer.get_scope()))

    def transform(self, record):
        # type: (Any) -> Any
        for t in self.transformers:
            record = t.transform(record)
            # Check filtered record
            if not record:
                return None

        return record

    def get_scope(self):
        # type: () -> str
        return 'transformer.chained'

    def close(self):
        # type: () -> None
        for t in self.transformers:
            t.close()
