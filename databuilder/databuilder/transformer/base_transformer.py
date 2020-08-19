# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc

from pyhocon import ConfigTree
from typing import Any, Iterable, Optional

from databuilder import Scoped


class Transformer(Scoped):
    """
    A transformer transforms a record
    """
    @abc.abstractmethod
    def init(self, conf: ConfigTree) -> None:
        pass

    @abc.abstractmethod
    def transform(self, record: Any) -> Any:
        pass


class NoopTransformer(Transformer):
    """
    A no-op transformer
    """

    def init(self, conf: ConfigTree) -> None:
        pass

    def transform(self, record: Any) -> Any:
        return record

    def get_scope(self) -> str:
        pass


class ChainedTransformer(Transformer):
    """
    A chained transformer that iterates transformers and transforms a record
    """

    def __init__(self,
                 transformers: Iterable[Transformer],
                 is_init_transformers: Optional[bool] = False) -> None:
        self.transformers = transformers
        self.is_init_transformers = is_init_transformers

    def init(self, conf: ConfigTree) -> None:
        if self.is_init_transformers:
            for transformer in self.transformers:
                transformer.init(Scoped.get_scoped_conf(conf, transformer.get_scope()))

    def transform(self, record: Any) -> Any:
        for t in self.transformers:
            record = t.transform(record)
            # Check filtered record
            if not record:
                return None

        return record

    def get_scope(self) -> str:
        return 'transformer.chained'

    def close(self) -> None:
        for t in self.transformers:
            t.close()
