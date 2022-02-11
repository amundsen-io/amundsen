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
    def test_hive_parser_usage(self) -> None:
        transformer = ComplexTypeTransformer()
        config = ConfigFactory.from_dict({
            PARSING_FUNCTION: 'databuilder.utils.hive_complex_type_parser.parse_hive_complex_type_string',
        })
        transformer.init(conf=config)

        table_metadata = TableMetadata(
            'hive',
            'gold',
            'test_schema',
            'test_table',
            'test_table',
            [
                ColumnMetadata('col1', 'array type', 'array<array<int>>', 0)
            ]
        )
        inner_scalar = ScalarTypeMetadata(data_type='int',
                                          type_str='int',
                                          start_label=TypeMetadata.NODE_LABEL,
                                          start_key='hive://gold.test_schema/test_table/col1/__array_inner'
                                                    '/__array_inner')
        inner_array = ArrayTypeMetadata(data_type=inner_scalar,
                                        type_str='array<int>',
                                        start_label=TypeMetadata.NODE_LABEL,
                                        start_key='hive://gold.test_schema/test_table/col1/__array_inner')
        array_type = ArrayTypeMetadata(data_type=inner_array,
                                       type_str='array<array<int>>',
                                       start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                       start_key='hive://gold.test_schema/test_table/col1')

        result = transformer.transform(table_metadata)

        for actual in result.columns:
            self.assertTrue(isinstance(actual.type_metadata, TypeMetadata))
            self.assertEqual(actual.type_metadata, array_type)


if __name__ == '__main__':
    unittest.main()
