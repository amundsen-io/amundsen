import abc

from pyhocon import ConfigTree  # noqa: F401

from databuilder import Scoped


class Publisher(Scoped):
    """
    A Publisher that writes dataset (not a record) in Atomic manner,
    if possible.
    (Either success or fail, no partial state)
    Use case: If you want to use neo4j import util or Load CSV util,
    that takes CSV file to load database, you need to first create CSV file.
    CSV file holds number of records, and loader can writes multiple records
    to it. Once loader finishes writing CSV file, you have complete CSV file,
    ready to publish to Neo4j. Publisher can take the location of CSV file,
    and push to Neo4j.

    """
    @abc.abstractmethod
    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    @abc.abstractmethod
    def publish(self):
        # type: () -> None
        pass

    def get_scope(self):
        # type: () -> str
        return 'publisher'


class NoopPublisher(Publisher):
    def __init__(self):
        # type: () -> None
        pass

    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    def publish(self):
        # type: () -> None
        pass

    def get_scope(self):
        # type: () -> str
        return 'publisher.noop'
