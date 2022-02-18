# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

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

    def test_hive_parser_usage(self) -> None:
        transformer = ComplexTypeTransformer()
        config = ConfigFactory.from_dict({
            PARSING_FUNCTION: 'databuilder.utils.hive_complex_type_parser.parse_hive_complex_type_string',
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
        inner_scalar = ScalarTypeMetadata(data_type='int',
                                          type_str='int')
        inner_array = ArrayTypeMetadata(data_type=inner_scalar,
                                        type_str='array<int>')
        array_type = ArrayTypeMetadata(data_type=inner_array,
                                       type_str='array<array<int>>')

        # Attributes set by the parser
        inner_scalar.name = '_inner_'
        inner_scalar.parent = inner_array
        inner_array.name = '_inner_'
        inner_array.parent = array_type
        array_type.name = 'type/col1'
        array_type.parent = column

        result = transformer.transform(table_metadata)

        for actual in result.columns:
            self.assertTrue(isinstance(actual.type_metadata, TypeMetadata))
            self.assertEqual(actual.type_metadata, array_type)


if __name__ == '__main__':
    unittest.main()
