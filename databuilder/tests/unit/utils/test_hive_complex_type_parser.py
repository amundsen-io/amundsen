# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from pyparsing import ParseException

from databuilder.models.table_metadata import ColumnMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata, MapTypeMetadata, ScalarTypeMetadata, StructTypeMetadata,
)
from databuilder.utils.hive_complex_type_parser import parse_hive_type


class TestHiveComplexTypeParser(unittest.TestCase):
    def setUp(self) -> None:
        self.column_key = 'hive://gold.test_schema/test_table/col1'

    def test_transform_no_complex_type(self) -> None:
        column = ColumnMetadata('col1', None, 'int', 0)
        column.set_column_key(self.column_key)

        scalar_type = ScalarTypeMetadata(name='col1',
                                         parent=column,
                                         type_str='int')

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, scalar_type)

    def test_transform_array_type(self) -> None:
        column = ColumnMetadata('col1', None, 'array<array<int>>', 0)
        column.set_column_key(self.column_key)

        array_type = ArrayTypeMetadata(name='col1',
                                       parent=column,
                                       type_str='array<array<int>>')
        inner_array = ArrayTypeMetadata(name='_inner_',
                                        parent=array_type,
                                        type_str='array<int>')

        array_type.array_inner_type = inner_array

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, array_type)

    def test_transform_array_map_nested_type(self) -> None:
        column = ColumnMetadata('col1', None, 'array<map<string,int>>', 0)
        column.set_column_key(self.column_key)

        array_type = ArrayTypeMetadata(name='col1',
                                       parent=column,
                                       type_str='array<map<string,int>>')
        inner_map = MapTypeMetadata(name='_inner_',
                                    parent=array_type,
                                    type_str='map<string,int>')
        inner_map_key = ScalarTypeMetadata(name='_map_key',
                                           parent=inner_map,
                                           type_str='string')
        inner_scalar = ScalarTypeMetadata(name='_map_value',
                                          parent=inner_map,
                                          type_str='int')

        array_type.array_inner_type = inner_map
        inner_map.map_key_type = inner_map_key
        inner_map.map_value_type = inner_scalar

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, array_type)

    def test_transform_array_struct_nested_type(self) -> None:
        column = ColumnMetadata('col1', None, 'array<struct<nest1:int,nest2:int>>', 0)
        column.set_column_key(self.column_key)

        array_type = ArrayTypeMetadata(name='col1',
                                       parent=column,
                                       type_str='array<struct<nest1:int,nest2:int>>')
        inner_struct = StructTypeMetadata(name='_inner_',
                                          parent=array_type,
                                          type_str='struct<nest1:int,nest2:int>')
        inner_scalar_nest1 = ScalarTypeMetadata(name='nest1',
                                                parent=inner_struct,
                                                type_str='int')
        inner_scalar_nest2 = ScalarTypeMetadata(name='nest2',
                                                parent=inner_struct,
                                                type_str='int')

        array_type.array_inner_type = inner_struct
        inner_struct.struct_items = {'nest1': inner_scalar_nest1, 'nest2': inner_scalar_nest2}
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.sort_order = 1

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, array_type)

    def test_transform_map_type(self) -> None:
        column = ColumnMetadata('col1', None, 'map<string,map<string,int>>', 0)
        column.set_column_key(self.column_key)

        map_type = MapTypeMetadata(name='col1',
                                   parent=column,
                                   type_str='map<string,map<string,int>>')
        map_key = ScalarTypeMetadata(name='_map_key',
                                     parent=map_type,
                                     type_str='string')
        map_value = MapTypeMetadata(name='_map_value',
                                    parent=map_type,
                                    type_str='map<string,int>')
        inner_map_key = ScalarTypeMetadata(name='_map_key',
                                           parent=map_value,
                                           type_str='string')
        inner_scalar = ScalarTypeMetadata(name='_map_value',
                                          parent=map_value,
                                          type_str='int')

        map_type.map_key_type = map_key
        map_type.map_value_type = map_value
        map_value.map_key_type = inner_map_key
        map_value.map_value_type = inner_scalar

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, map_type)

    def test_transform_map_struct_nested_type(self) -> None:
        column = ColumnMetadata('col1', None, 'map<string,struct<nest1:int,nest2:int>>', 0)
        column.set_column_key(self.column_key)

        map_type = MapTypeMetadata(name='col1',
                                   parent=column,
                                   type_str='map<string,struct<nest1:int,nest2:int>>')
        map_key = ScalarTypeMetadata(name='_map_key',
                                     parent=map_type,
                                     type_str='string')
        inner_struct = StructTypeMetadata(name='_map_value',
                                          parent=map_type,
                                          type_str='struct<nest1:int,nest2:int>')
        inner_scalar_nest1 = ScalarTypeMetadata(name='nest1',
                                                parent=inner_struct,
                                                type_str='int')
        inner_scalar_nest2 = ScalarTypeMetadata(name='nest2',
                                                parent=inner_struct,
                                                type_str='int')

        map_type.map_key_type = map_key
        map_type.map_value_type = inner_struct
        inner_struct.struct_items = {'nest1': inner_scalar_nest1, 'nest2': inner_scalar_nest2}
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.sort_order = 1

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, map_type)

    def test_transform_struct_type(self) -> None:
        column = ColumnMetadata('col1', None, 'struct<nest1:int,nest2:int>', 0)
        column.set_column_key(self.column_key)

        struct_type = StructTypeMetadata(name='col1',
                                         parent=column,
                                         type_str='struct<nest1:int,nest2:int>')
        inner_scalar_nest1 = ScalarTypeMetadata(name='nest1',
                                                parent=struct_type,
                                                type_str='int')
        inner_scalar_nest2 = ScalarTypeMetadata(name='nest2',
                                                parent=struct_type,
                                                type_str='int')

        struct_type.struct_items = {'nest1': inner_scalar_nest1, 'nest2': inner_scalar_nest2}
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.sort_order = 1

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, struct_type)

    def test_transform_struct_map_array_nested_type(self) -> None:
        column = ColumnMetadata('col1', None, 'struct<nest1:map<string,array<int>>,nest2:array<string>>', 0)
        column.set_column_key(self.column_key)

        struct_type = StructTypeMetadata(name='col1',
                                         parent=column,
                                         type_str='struct<nest1:map<string,array<int>>,nest2:array<string>>')
        inner_map = MapTypeMetadata(name='nest1',
                                    parent=struct_type,
                                    type_str='map<string,array<int>>')
        inner_map_key = ScalarTypeMetadata(name='_map_key',
                                           parent=inner_map,
                                           type_str='string')
        inner_map_array = ArrayTypeMetadata(name='_map_value',
                                            parent=inner_map,
                                            type_str='array<int>')
        inner_struct_array = ArrayTypeMetadata(name='nest2',
                                               parent=struct_type,
                                               type_str='array<string>')

        struct_type.struct_items = {'nest1': inner_map, 'nest2': inner_struct_array}
        inner_map.map_key_type = inner_map_key
        inner_map.map_value_type = inner_map_array
        inner_map.sort_order = 0
        inner_struct_array.sort_order = 1

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, struct_type)

    def test_transform_non_alpha_only_types(self) -> None:
        column = ColumnMetadata('col1', None, 'struct<nest1:decimal(10,2),nest2:double precision,'
                                              'nest3:varchar(32),nest4:map<varchar(32),decimal(10,2)>,'
                                              'nest5:interval_day_time>', 0)
        column.set_column_key(self.column_key)

        struct_type = StructTypeMetadata(name='col1',
                                         parent=column,
                                         type_str='struct<nest1:decimal(10,2),nest2:double precision,'
                                                  'nest3:varchar(32),nest4:map<varchar(32),decimal(10,2)>,'
                                                  'nest5:interval_day_time>')
        inner_scalar_nest1 = ScalarTypeMetadata(name='nest1',
                                                parent=struct_type,
                                                type_str='decimal(10,2)')
        inner_scalar_nest2 = ScalarTypeMetadata(name='nest2',
                                                parent=struct_type,
                                                type_str='double precision')
        inner_scalar_nest3 = ScalarTypeMetadata(name='nest3',
                                                parent=struct_type,
                                                type_str='varchar(32)')
        inner_map_nest4 = MapTypeMetadata(name='nest4',
                                          parent=struct_type,
                                          type_str='map<varchar(32),decimal(10,2)>')
        inner_map_nest4_key = ScalarTypeMetadata(name='_map_key',
                                                 parent=inner_map_nest4,
                                                 type_str='varchar(32)')
        inner_map_nest4_value = ScalarTypeMetadata(name='_map_value',
                                                   parent=inner_map_nest4,
                                                   type_str='decimal(10,2)')
        inner_scalar_nest5 = ScalarTypeMetadata(name='nest5',
                                                parent=struct_type,
                                                type_str='interval_day_time')

        struct_type.struct_items = {'nest1': inner_scalar_nest1, 'nest2': inner_scalar_nest2,
                                    'nest3': inner_scalar_nest3, 'nest4': inner_map_nest4,
                                    'nest5': inner_scalar_nest5}
        inner_map_nest4.map_key_type = inner_map_nest4_key
        inner_map_nest4.map_value_type = inner_map_nest4_value
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.sort_order = 1
        inner_scalar_nest3.sort_order = 2
        inner_map_nest4.sort_order = 3
        inner_scalar_nest5.sort_order = 4

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, struct_type)

    def test_transform_union_as_scalar_type(self) -> None:
        column = ColumnMetadata('col1', None, 'uniontype<string,struct<c1:int,c2:string>>', 0)
        column.set_column_key(self.column_key)

        struct_type = ScalarTypeMetadata(name='col1',
                                         parent=column,
                                         type_str='uniontype<string,struct<c1:int,c2:string>>')

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, struct_type)

    def test_transform_union_as_nested_type(self) -> None:
        column = ColumnMetadata('col1', None, 'struct<nest1:uniontype<string,struct<c1:int,c2:string>>,'
                                              'nest2:uniontype<string,int>>', 0)
        column.set_column_key(self.column_key)

        struct_type = StructTypeMetadata(name='col1',
                                         parent=column,
                                         type_str='struct<nest1:uniontype<string,struct<c1:int,c2:string>>,'
                                                  'nest2:uniontype<string,int>>')
        inner_scalar_nest1 = ScalarTypeMetadata(name='nest1',
                                                parent=struct_type,
                                                type_str='uniontype<string,struct<c1:int,c2:string>>')
        inner_scalar_nest2 = ScalarTypeMetadata(name='nest2',
                                                parent=struct_type,
                                                type_str='uniontype<string,int>')

        struct_type.struct_items = {'nest1': inner_scalar_nest1, 'nest2': inner_scalar_nest2}
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.sort_order = 1

        actual = parse_hive_type(column.type, column.name, column)
        self.assertEqual(actual, struct_type)

    def test_transform_invalid_array_inner_type(self) -> None:
        column = ColumnMetadata('col1', None, 'array<array<int*>>', 0)
        column.set_column_key(self.column_key)

        with self.assertRaises(ParseException):
            parse_hive_type(column.type, column.name, column)

    def test_transform_invalid_struct_inner_type(self) -> None:
        column = ColumnMetadata('col1', None, 'struct<nest1:varchar(256)å,'
                                              'nest2:<derived from deserializer>>', 0)
        column.set_column_key(self.column_key)

        with self.assertRaises(ParseException):
            parse_hive_type(column.type, column.name, column)


if __name__ == '__main__':
    unittest.main()
