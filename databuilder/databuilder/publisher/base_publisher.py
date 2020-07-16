# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc

from pyhocon import ConfigTree  # noqa: F401

from databuilder import Scoped
from databuilder.callback import call_back
from databuilder.callback.call_back import Callback  # noqa: F401


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

    def __init__(self):
        self.call_backs = []  # type: List[Callback]

    @abc.abstractmethod
    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    def publish(self):
        try:
            self.publish_impl()
        except Exception as e:
            call_back.notify_callbacks(self.call_backs, is_success=False)
            raise e
        call_back.notify_callbacks(self.call_backs, is_success=True)

    @abc.abstractmethod
    def publish_impl(self):
        # type: () -> None
        """
        An implementation of publish method. Subclass of publisher is expected to write publish logic by overriding
        this method
        :return: None
        """
        pass

    def register_call_back(self, callback):
        # type: (Callback) -> None
        """
        Register any callback method that needs to be notified when publisher is either able to successfully publish
        or failed to publish
        :param callback:
        :return: None
        """
        self.call_backs.append(callback)

    def get_scope(self):
        # type: () -> str
        return 'publisher'


class NoopPublisher(Publisher):
    def __init__(self):
        # type: () -> None
        super(NoopPublisher, self).__init__()

    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    def publish_impl(self):
        # type: () -> None
        pass

    def get_scope(self):
        # type: () -> str
        return 'publisher.noop'
