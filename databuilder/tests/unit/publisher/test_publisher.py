# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from mock import MagicMock

from databuilder.publisher.base_publisher import Publisher, NoopPublisher


class TestPublisher(unittest.TestCase):

    def testCallback(self):
        # type: () -> None

        publisher = NoopPublisher()
        callback = MagicMock()
        publisher.register_call_back(callback)
        publisher.publish()

        self.assertTrue(callback.on_success.called)

    def testFailureCallback(self):
        # type: () -> None

        publisher = FailedPublisher()
        callback = MagicMock()
        publisher.register_call_back(callback)

        try:
            publisher.publish()
        except Exception:
            pass

        self.assertTrue(callback.on_failure.called)


class FailedPublisher(Publisher):

    def __init__(self):
        # type: () -> None
        super(FailedPublisher, self).__init__()

    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    def publish_impl(self):
        # type: () -> None
        raise Exception('Bomb')


if __name__ == '__main__':
    unittest.main()
