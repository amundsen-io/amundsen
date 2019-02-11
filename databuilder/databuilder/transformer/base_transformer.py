import abc

from pyhocon import ConfigTree  # noqa: F401
from typing import Any, Iterable  # noqa: F401

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
    def __init__(self, transformers):
        # type: (Iterable[Transformer]) -> None
        self.transformers = transformers

    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

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
        pass

    def close(self):
        # type: () -> None
        for t in self.transformers:
            t.close()
