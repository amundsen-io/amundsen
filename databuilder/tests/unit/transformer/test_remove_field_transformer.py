# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from pyhocon import ConfigFactory

from databuilder.transformer.remove_field_transformer import RemoveFieldTransformer, FIELD_NAMES


class TestRemoveFieldTransformer(unittest.TestCase):

    def test_conversion(self):
        # type: () -> None

        transformer = RemoveFieldTransformer()
        config = ConfigFactory.from_dict({
            FIELD_NAMES: ['foo', 'bar'],
        })
        transformer.init(conf=config)

        actual = transformer.transform({
            'foo': 'foo_val',
            'bar': 'bar_val',
            'baz': 'baz_val',
        })
        expected = {
            'baz': 'baz_val'
        }
        self.assertDictEqual(expected, actual)

    def test_conversion_missing_field(self):
        # type: () -> None

        transformer = RemoveFieldTransformer()
        config = ConfigFactory.from_dict({
            FIELD_NAMES: ['foo', 'bar'],
        })
        transformer.init(conf=config)

        actual = transformer.transform({
            'foo': 'foo_val',
            'baz': 'baz_val',
            'john': 'doe',
        })
        expected = {
            'baz': 'baz_val',
            'john': 'doe'
        }
        self.assertDictEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
