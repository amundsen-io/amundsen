# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from pyhocon import ConfigFactory

from databuilder.transformer.timestamp_string_to_epoch import TimestampStringToEpoch, FIELD_NAME, TIMESTAMP_FORMAT


class TestTimestampStrToEpoch(unittest.TestCase):

    def test_conversion(self):
        # type: () -> None

        transformer = TimestampStringToEpoch()
        config = ConfigFactory.from_dict({
            FIELD_NAME: 'foo',
        })
        transformer.init(conf=config)

        actual = transformer.transform({'foo': '2020-02-19T19:52:33.1Z'})
        self.assertDictEqual({'foo': 1582141953}, actual)

    def test_conversion_with_format(self):
        # type: () -> None

        transformer = TimestampStringToEpoch()
        config = ConfigFactory.from_dict({
            FIELD_NAME: 'foo',
            TIMESTAMP_FORMAT: '%Y-%m-%dT%H:%M:%SZ'
        })
        transformer.init(conf=config)

        actual = transformer.transform({'foo': '2020-02-19T19:52:33Z'})
        self.assertDictEqual({'foo': 1582141953}, actual)


if __name__ == '__main__':
    unittest.main()
