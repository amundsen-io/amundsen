# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock, patch

from pyhocon import ConfigFactory

from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata, ScalarTypeMetadata, TypeMetadata,
)
from databuilder.transformer.complex_type_transformer import PARSING_FUNCTION, ComplexTypeTransformer


class TestComplexTypeTransformer(unittest.TestCase):
    def test_invalid_parsing_function_missing_module(self) -> None:
        transformer = ComplexTypeTransformer()
        config = ConfigFactory.from_dict({
            PARSING_FUNCTION: 'invalid_function',
        })
        with self.assertRaises(Exception):
            transformer.init(conf=config)

    def test_invalid_parsing_function_invalid_module(self) -> None:
        transformer = ComplexTypeTransformer()
        config = ConfigFactory.from_dict({
            PARSING_FUNCTION: 'invalid_module.invalid_function',
        })
        with self.assertRaises(Exception):
            transformer.init(conf=config)

    def test_invalid_parsing_function_invalid_function(self) -> None:
        transformer = ComplexTypeTransformer()
        config = ConfigFactory.from_dict({
            PARSING_FUNCTION: 'databuilder.utils.hive_complex_type_parser.invalid_function',
        })
        with self.assertRaises(Exception):
            transformer.init(conf=config)

    def test_hive_parser_with_failures(self) -> None:
        transformer = ComplexTypeTransformer()
        config = ConfigFactory.from_dict({
            PARSING_FUNCTION: 'databuilder.utils.hive_complex_type_parser.parse_hive_type',
        })
        transformer.init(conf=config)

        column = ColumnMetadata('col1', 'array type', 'array<array<int>>', 0)
        table_metadata = TableMetadata(
            'hive',
            'gold',
            'test_schema',
            'test_table',
            'test_table',
            [column]
        )

        default_scalar_type = ScalarTypeMetadata(name='col1',
                                                 parent=column,
                                                 type_str='array<array<int>>')

        with patch.object(transformer, '_parsing_function') as mock:
            mock.side_effect = MagicMock(side_effect=Exception('Could not parse'))

            result = transformer.transform(table_metadata)

            self.assertEqual(transformer.success_count, 0)
            self.assertEqual(transformer.failure_count, 1)
            for actual in result.columns:
                self.assertEqual(actual.get_type_metadata(), default_scalar_type)

    def test_hive_parser_usage(self) -> None:
        transformer = ComplexTypeTransformer()
        config = ConfigFactory.from_dict({
            PARSING_FUNCTION: 'databuilder.utils.hive_complex_type_parser.parse_hive_type',
        })
        transformer.init(conf=config)

        column = ColumnMetadata('col1', 'array type', 'array<array<int>>', 0)
        table_metadata = TableMetadata(
            'hive',
            'gold',
            'test_schema',
            'test_table',
            'test_table',
            [column]
        )
        array_type = ArrayTypeMetadata(name='col1',
                                       parent=column,
                                       type_str='array<array<int>>')
        inner_array = ArrayTypeMetadata(name='_inner_',
                                        parent=array_type,
                                        type_str='array<int>')

        array_type.array_inner_type = inner_array

        result = transformer.transform(table_metadata)

        for actual in result.columns:
            self.assertTrue(isinstance(actual.get_type_metadata(), TypeMetadata))
            self.assertEqual(actual.get_type_metadata(), array_type)
            self.assertEqual(transformer.success_count, 1)
            self.assertEqual(transformer.failure_count, 0)


if __name__ == '__main__':
    unittest.main()
