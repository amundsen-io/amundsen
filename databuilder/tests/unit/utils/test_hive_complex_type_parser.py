# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.table_metadata import ColumnMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata, MapTypeMetadata, ScalarTypeMetadata, StructTypeMetadata,
)
from databuilder.utils.hive_complex_type_parser import parse_hive_complex_type_string


class TestHiveComplexTypeParser(unittest.TestCase):
    def setUp(self) -> None:
        self.column_key = 'hive://gold.test_schema/test_table/col1'

    def test_transform_no_complex_type(self) -> None:
        column = ColumnMetadata('col1', None, 'int', 0)
        column.column_key = self.column_key

        actual = parse_hive_complex_type_string(column)
        self.assertIsNone(actual)

    def test_transform_array_type(self) -> None:
        inner_scalar = ScalarTypeMetadata(data_type='int',
                                          type_str='int')
        inner_array = ArrayTypeMetadata(data_type=inner_scalar,
                                        type_str='array<int>')
        array_type = ArrayTypeMetadata(data_type=inner_array,
                                       type_str='array<array<int>>')

        column = ColumnMetadata('col1', None, 'array<array<int>>', 0)
        column.column_key = self.column_key

        # Attributes set by the parser
        inner_scalar.name = '_inner_'
        inner_scalar.parent = inner_array
        inner_array.name = '_inner_'
        inner_array.parent = array_type
        array_type.name = 'type/col1'
        array_type.parent = column

        actual = parse_hive_complex_type_string(column)
        self.assertEqual(actual, array_type)

    def test_transform_array_map_nested_type(self) -> None:
        inner_scalar = ScalarTypeMetadata(data_type='int',
                                          type_str='int')
        inner_map_key = ScalarTypeMetadata(data_type='string',
                                           type_str='string')
        inner_map = MapTypeMetadata(map_key=inner_map_key,
                                    map_value=inner_scalar,
                                    type_str='map<string,int>')
        array_type = ArrayTypeMetadata(data_type=inner_map,
                                       type_str='array<map<string,int>>')

        column = ColumnMetadata('col1', None, 'array<map<string,int>>', 0)
        column.column_key = self.column_key

        # Attributes set by the parser
        inner_scalar.name = '_map_value'
        inner_scalar.parent = inner_map
        inner_map_key.name = '_map_key'
        inner_map_key.parent = inner_map
        inner_map.name = '_inner_'
        inner_map.parent = array_type
        array_type.name = 'type/col1'
        array_type.parent = column

        actual = parse_hive_complex_type_string(column)
        self.assertEqual(actual, array_type)

    def test_transform_array_struct_nested_type(self) -> None:
        inner_scalar_nest1 = ScalarTypeMetadata(data_type='int',
                                                type_str='int')
        inner_scalar_nest2 = ScalarTypeMetadata(data_type='int',
                                                type_str='int')
        inner_struct = StructTypeMetadata(struct_items={'nest1': inner_scalar_nest1,
                                                        'nest2': inner_scalar_nest2},
                                          type_str='struct<nest1:int,nest2:int>')
        array_type = ArrayTypeMetadata(data_type=inner_struct,
                                       type_str='array<struct<nest1:int,nest2:int>>')

        column = ColumnMetadata('col1', None, 'array<struct<nest1:int,nest2:int>>', 0)
        column.column_key = self.column_key

        # Attributes set by the parser
        inner_scalar_nest1.name = 'nest1'
        inner_scalar_nest1.parent = inner_struct
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.name = 'nest2'
        inner_scalar_nest2.parent = inner_struct
        inner_scalar_nest2.sort_order = 1
        inner_struct.name = '_inner_'
        inner_struct.parent = array_type
        array_type.name = 'type/col1'
        array_type.parent = column

        actual = parse_hive_complex_type_string(column)
        self.assertEqual(actual, array_type)

    def test_transform_map_type(self) -> None:
        inner_scalar = ScalarTypeMetadata(data_type='int',
                                          type_str='int')
        inner_map_key = ScalarTypeMetadata(data_type='string',
                                           type_str='string')
        map_value = MapTypeMetadata(map_key=inner_map_key,
                                    map_value=inner_scalar,
                                    type_str='map<string,int>')
        map_key = ScalarTypeMetadata(data_type='string',
                                     type_str='string')
        map_type = MapTypeMetadata(map_key=map_key,
                                   map_value=map_value,
                                   type_str='map<string,map<string,int>>')

        column = ColumnMetadata('col1', None, 'map<string,map<string,int>>', 0)
        column.column_key = self.column_key

        # Attributes set by the parser
        inner_scalar.name = '_map_value'
        inner_scalar.parent = map_value
        inner_map_key.name = '_map_key'
        inner_map_key.parent = map_value
        map_value.name = '_map_value'
        map_value.parent = map_type
        map_key.name = '_map_key'
        map_key.parent = map_type
        map_type.name = 'type/col1'
        map_type.parent = column

        actual = parse_hive_complex_type_string(column)
        self.assertEqual(actual, map_type)

    def test_transform_map_struct_nested_type(self) -> None:
        inner_scalar_nest1 = ScalarTypeMetadata(data_type='int',
                                                type_str='int')
        inner_scalar_nest2 = ScalarTypeMetadata(data_type='int',
                                                type_str='int')
        inner_struct = StructTypeMetadata(struct_items={'nest1': inner_scalar_nest1,
                                                        'nest2': inner_scalar_nest2},
                                          type_str='struct<nest1:int,nest2:int>')
        map_key = ScalarTypeMetadata(data_type='string',
                                     type_str='string')
        map_type = MapTypeMetadata(map_key=map_key,
                                   map_value=inner_struct,
                                   type_str='map<string,struct<nest1:int,nest2:int>>')

        column = ColumnMetadata('col1', None, 'map<string,struct<nest1:int,nest2:int>>', 0)
        column.column_key = self.column_key

        # Attributes set by the parser
        inner_scalar_nest1.name = 'nest1'
        inner_scalar_nest1.parent = inner_struct
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.name = 'nest2'
        inner_scalar_nest2.parent = inner_struct
        inner_scalar_nest2.sort_order = 1
        inner_struct.name = '_map_value'
        inner_struct.parent = map_type
        map_key.name = '_map_key'
        map_key.parent = map_type
        map_type.name = 'type/col1'
        map_type.parent = column

        actual = parse_hive_complex_type_string(column)
        self.assertEqual(actual, map_type)

    def test_transform_struct_type(self) -> None:
        inner_scalar_nest1 = ScalarTypeMetadata(data_type='int',
                                                type_str='int')
        inner_scalar_nest2 = ScalarTypeMetadata(data_type='int',
                                                type_str='int')
        struct_type = StructTypeMetadata(struct_items={'nest1': inner_scalar_nest1,
                                                       'nest2': inner_scalar_nest2},
                                         type_str='struct<nest1:int,nest2:int>')

        column = ColumnMetadata('col1', None, 'struct<nest1:int,nest2:int>', 0)
        column.column_key = self.column_key

        # Attributes set by the parser
        inner_scalar_nest1.name = 'nest1'
        inner_scalar_nest1.parent = struct_type
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.name = 'nest2'
        inner_scalar_nest2.parent = struct_type
        inner_scalar_nest2.sort_order = 1
        struct_type.name = 'type/col1'
        struct_type.parent = column

        actual = parse_hive_complex_type_string(column)
        self.assertEqual(actual, struct_type)

    def test_transform_struct_map_array_nested_type(self) -> None:
        inner_scalar_nest1 = ScalarTypeMetadata(data_type='int',
                                                type_str='int')
        inner_scalar_nest2 = ScalarTypeMetadata(data_type='string',
                                                type_str='string')
        inner_map_array = ArrayTypeMetadata(data_type=inner_scalar_nest1,
                                            type_str='array<int>')
        inner_map_key = ScalarTypeMetadata(data_type='string',
                                           type_str='string')
        inner_map = MapTypeMetadata(map_key=inner_map_key,
                                    map_value=inner_map_array,
                                    type_str='map<string,array<int>>')
        inner_struct_array = ArrayTypeMetadata(data_type=inner_scalar_nest2,
                                               type_str='array<string>')
        struct_type = StructTypeMetadata(struct_items={'nest1': inner_map,
                                                       'nest2': inner_struct_array},
                                         type_str='struct<nest1:map<string,array<int>>,nest2:array<string>>')

        column = ColumnMetadata('col1', None, 'struct<nest1:map<string,array<int>>,nest2:array<string>>', 0)
        column.column_key = self.column_key

        # Attributes set by the parser
        inner_scalar_nest1.name = '_inner_'
        inner_scalar_nest1.parent = inner_map_array
        inner_scalar_nest2.name = '_inner_'
        inner_scalar_nest2.parent = inner_struct_array
        inner_map_array.name = '_map_value'
        inner_map_array.parent = inner_map
        inner_map_key.name = '_map_key'
        inner_map_key.parent = inner_map
        inner_map.name = 'nest1'
        inner_map.parent = struct_type
        inner_map.sort_order = 0
        inner_struct_array.name = 'nest2'
        inner_struct_array.parent = struct_type
        inner_struct_array.sort_order = 1
        struct_type.name = 'type/col1'
        struct_type.parent = column

        actual = parse_hive_complex_type_string(column)
        self.assertEqual(actual, struct_type)


if __name__ == '__main__':
    unittest.main()
