# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.table_metadata import ColumnMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata, MapTypeMetadata, ScalarTypeMetadata, StructTypeMetadata, TypeMetadata,
)
from databuilder.utils.hive_complex_type_parser import parse_hive_complex_type_string


class TestHiveComplexTypeParser(unittest.TestCase):
    def setUp(self) -> None:
        self.column_key = 'hive://gold.test_schema/test_table/col1'

    def test_transform_no_complex_type(self) -> None:
        actual = parse_hive_complex_type_string('int', self.column_key)
        self.assertIsNone(actual)

    def test_transform_array_type(self) -> None:
        inner_scalar = ScalarTypeMetadata(data_type='int',
                                          type_str='int',
                                          start_label=TypeMetadata.NODE_LABEL,
                                          start_key='hive://gold.test_schema/test_table/col1'
                                                    '/__array_inner/__array_inner')
        inner_array = ArrayTypeMetadata(data_type=inner_scalar,
                                        type_str='array<int>',
                                        start_label=TypeMetadata.NODE_LABEL,
                                        start_key='hive://gold.test_schema/test_table/col1/__array_inner')
        array_type = ArrayTypeMetadata(data_type=inner_array,
                                       type_str='array<array<int>>',
                                       start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                       start_key='hive://gold.test_schema/test_table/col1')

        actual = parse_hive_complex_type_string('array<array<int>>', self.column_key)
        self.assertEqual(actual, array_type)

    def test_transform_array_map_nested_type(self) -> None:
        inner_scalar = ScalarTypeMetadata(data_type='int',
                                          type_str='int',
                                          start_label=TypeMetadata.NODE_LABEL,
                                          start_key='hive://gold.test_schema/test_table/col1'
                                                    '/__array_inner/__map_inner')
        inner_map = MapTypeMetadata(key='string',
                                    value=inner_scalar,
                                    type_str='map<string,int>',
                                    start_label=TypeMetadata.NODE_LABEL,
                                    start_key='hive://gold.test_schema/test_table/col1/__array_inner')
        array_type = ArrayTypeMetadata(data_type=inner_map,
                                       type_str='array<map<string,int>>',
                                       start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                       start_key='hive://gold.test_schema/test_table/col1')

        actual = parse_hive_complex_type_string('array<map<string,int>>', self.column_key)
        self.assertEqual(actual, array_type)

    def test_transform_array_struct_nested_type(self) -> None:
        inner_scalar_nest1 = ScalarTypeMetadata(data_type='int',
                                                type_str='int',
                                                start_label=TypeMetadata.NODE_LABEL,
                                                start_key='hive://gold.test_schema/test_table/col1/__array_inner/nest1')
        inner_scalar_nest2 = ScalarTypeMetadata(data_type='int',
                                                type_str='int',
                                                start_label=TypeMetadata.NODE_LABEL,
                                                start_key='hive://gold.test_schema/test_table/col1/__array_inner/nest2')
        inner_struct = StructTypeMetadata(struct_items={'nest1': inner_scalar_nest1,
                                                        'nest2': inner_scalar_nest2},
                                          type_str='struct<nest1:int,nest2:int>',
                                          start_label=TypeMetadata.NODE_LABEL,
                                          start_key='hive://gold.test_schema/test_table/col1/__array_inner')
        array_type = ArrayTypeMetadata(data_type=inner_struct,
                                       type_str='array<struct<nest1:int,nest2:int>>',
                                       start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                       start_key='hive://gold.test_schema/test_table/col1')

        actual = parse_hive_complex_type_string('array<struct<nest1:int,nest2:int>>', self.column_key)
        self.assertEqual(actual, array_type)

    def test_transform_map_type(self) -> None:
        inner_scalar = ScalarTypeMetadata(data_type='int',
                                          type_str='int',
                                          start_label=TypeMetadata.NODE_LABEL,
                                          start_key='hive://gold.test_schema/test_table/col1/__map_inner/__map_inner')
        inner_map = MapTypeMetadata(key='string',
                                    value=inner_scalar,
                                    type_str='map<string,int>',
                                    start_label=TypeMetadata.NODE_LABEL,
                                    start_key='hive://gold.test_schema/test_table/col1/__map_inner')
        map_type = MapTypeMetadata(key='string',
                                   value=inner_map,
                                   type_str='map<string,map<string,int>>',
                                   start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                   start_key='hive://gold.test_schema/test_table/col1')

        actual = parse_hive_complex_type_string('map<string,map<string,int>>', self.column_key)
        self.assertEqual(actual, map_type)

    def test_transform_map_struct_nested_type(self) -> None:
        inner_scalar_nest1 = ScalarTypeMetadata(data_type='int',
                                                type_str='int',
                                                start_label=TypeMetadata.NODE_LABEL,
                                                start_key='hive://gold.test_schema/test_table/col1/__map_inner/nest1')
        inner_scalar_nest2 = ScalarTypeMetadata(data_type='int',
                                                type_str='int',
                                                start_label=TypeMetadata.NODE_LABEL,
                                                start_key='hive://gold.test_schema/test_table/col1/__map_inner/nest2')
        inner_struct = StructTypeMetadata(struct_items={'nest1': inner_scalar_nest1,
                                                        'nest2': inner_scalar_nest2},
                                          type_str='struct<nest1:int,nest2:int>',
                                          start_label=TypeMetadata.NODE_LABEL,
                                          start_key='hive://gold.test_schema/test_table/col1/__map_inner')
        map_type = MapTypeMetadata(key='string',
                                   value=inner_struct,
                                   type_str='map<string,struct<nest1:int,nest2:int>>',
                                   start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                   start_key='hive://gold.test_schema/test_table/col1')

        actual = parse_hive_complex_type_string('map<string,struct<nest1:int,nest2:int>>', self.column_key)
        self.assertEqual(actual, map_type)

    def test_transform_struct_type(self) -> None:
        inner_scalar_nest1 = ScalarTypeMetadata(data_type='int',
                                                type_str='int',
                                                start_label=TypeMetadata.NODE_LABEL,
                                                start_key='hive://gold.test_schema/test_table/col1/nest1')
        inner_scalar_nest2 = ScalarTypeMetadata(data_type='int',
                                                type_str='int',
                                                start_label=TypeMetadata.NODE_LABEL,
                                                start_key='hive://gold.test_schema/test_table/col1/nest2')
        struct_type = StructTypeMetadata(struct_items={'nest1': inner_scalar_nest1,
                                                       'nest2': inner_scalar_nest2},
                                         type_str='struct<nest1:int,nest2:int>',
                                         start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                         start_key='hive://gold.test_schema/test_table/col1')

        actual = parse_hive_complex_type_string('struct<nest1:int,nest2:int>', self.column_key)
        self.assertEqual(actual, struct_type)

    def test_transform_struct_map_array_nested_type(self) -> None:
        inner_scalar_nest1 = ScalarTypeMetadata(data_type='int',
                                                type_str='int',
                                                start_label=TypeMetadata.NODE_LABEL,
                                                start_key='hive://gold.test_schema/test_table/col1/nest1'
                                                          '/__map_inner/__array_inner')
        inner_scalar_nest2 = ScalarTypeMetadata(data_type='string',
                                                type_str='string',
                                                start_label=TypeMetadata.NODE_LABEL,
                                                start_key='hive://gold.test_schema/test_table/col1/nest2/__array_inner')
        inner_map_array = ArrayTypeMetadata(data_type=inner_scalar_nest1,
                                            type_str='array<int>',
                                            start_label=TypeMetadata.NODE_LABEL,
                                            start_key='hive://gold.test_schema/test_table/col1/nest1/__map_inner')
        inner_map = MapTypeMetadata(key='string',
                                    value=inner_map_array,
                                    type_str='map<string,array<int>>',
                                    start_label=TypeMetadata.NODE_LABEL,
                                    start_key='hive://gold.test_schema/test_table/col1/nest1')
        inner_struct_array = ArrayTypeMetadata(data_type=inner_scalar_nest2,
                                               type_str='array<string>',
                                               start_label=TypeMetadata.NODE_LABEL,
                                               start_key='hive://gold.test_schema/test_table/col1/nest2')
        struct_type = StructTypeMetadata(struct_items={'nest1': inner_map,
                                                       'nest2': inner_struct_array},
                                         type_str='struct<nest1:map<string,array<int>>,nest2:array<string>>',
                                         start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                         start_key='hive://gold.test_schema/test_table/col1')

        actual = parse_hive_complex_type_string('struct<nest1:map<string,array<int>>,nest2:array<string>>',
                                                self.column_key)
        self.assertEqual(actual, struct_type)


if __name__ == '__main__':
    unittest.main()
