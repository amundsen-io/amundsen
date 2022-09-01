# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from pyparsing import ParseException

from databuilder.models.table_metadata import ColumnMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata, ScalarTypeMetadata, StructTypeMetadata,
)
from databuilder.utils.event_bridge_complex_type_parser import parse_event_bridge_type


class TestEventBridgeComplexTypeParser(unittest.TestCase):
    def setUp(self) -> None:
        self.column_key = (
            "eventbridge://gold.test_schema/test_table/col1"  # change to eventbridge
        )

    def test_transform_no_complex_type(self) -> None:
        column = ColumnMetadata("col1", None, "int", 0)
        column.set_column_key(self.column_key)

        scalar_type = ScalarTypeMetadata(name="col1", parent=column, type_str="int")

        actual = parse_event_bridge_type(column.type, column.name, column)
        self.assertEqual(actual, scalar_type)

    def test_transform_scalar_type(self) -> None:
        column = ColumnMetadata("col1", None, "string", 0)
        column.set_column_key(self.column_key)

        scalar_type = ScalarTypeMetadata(name="col1", parent=column, type_str="string")

        actual = parse_event_bridge_type(column.type, column.name, column)
        self.assertEqual(actual, scalar_type)

    def test_transform_additive_scalar_type(self) -> None:
        column = ColumnMetadata("col1", None, "string[date-time]", 0)
        column.set_column_key(self.column_key)

        scalar_type = ScalarTypeMetadata(
            name="col1", parent=column, type_str="string[date-time]"
        )

        actual = parse_event_bridge_type(column.type, column.name, column)
        self.assertEqual(actual, scalar_type)

    def test_transform_array_type(self) -> None:
        column = ColumnMetadata("col1", None, "array<array<int>>", 0)
        column.set_column_key(self.column_key)

        array_type = ArrayTypeMetadata(
            name="col1", parent=column, type_str="array<array<int>>"
        )
        inner_array = ArrayTypeMetadata(
            name="_inner_", parent=array_type, type_str="array<int>"
        )

        array_type.array_inner_type = inner_array

        actual = parse_event_bridge_type(column.type, column.name, column)
        self.assertEqual(actual, array_type)

    def test_transform_array_struct_nested_type(self) -> None:
        column = ColumnMetadata("col1", None, "array<struct<nest1:int,nest2:int>>", 0)
        column.set_column_key(self.column_key)

        array_type = ArrayTypeMetadata(
            name="col1", parent=column, type_str="array<struct<nest1:int,nest2:int>>"
        )
        inner_struct = StructTypeMetadata(
            name="_inner_", parent=array_type, type_str="struct<nest1:int,nest2:int>"
        )
        inner_scalar_nest1 = ScalarTypeMetadata(
            name="nest1", parent=inner_struct, type_str="int"
        )
        inner_scalar_nest2 = ScalarTypeMetadata(
            name="nest2", parent=inner_struct, type_str="int"
        )

        array_type.array_inner_type = inner_struct
        inner_struct.struct_items = {
            "nest1": inner_scalar_nest1,
            "nest2": inner_scalar_nest2,
        }
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.sort_order = 1

        actual = parse_event_bridge_type(column.type, column.name, column)
        self.assertEqual(actual, array_type)

    def test_transform_struct_type(self) -> None:
        column = ColumnMetadata("col1", None, "struct<nest1:int,nest2:int>", 0)
        column.set_column_key(self.column_key)

        struct_type = StructTypeMetadata(
            name="col1", parent=column, type_str="struct<nest1:int,nest2:int>"
        )
        inner_scalar_nest1 = ScalarTypeMetadata(
            name="nest1", parent=struct_type, type_str="int"
        )
        inner_scalar_nest2 = ScalarTypeMetadata(
            name="nest2", parent=struct_type, type_str="int"
        )

        struct_type.struct_items = {
            "nest1": inner_scalar_nest1,
            "nest2": inner_scalar_nest2,
        }
        inner_scalar_nest1.sort_order = 0
        inner_scalar_nest2.sort_order = 1

        actual = parse_event_bridge_type(column.type, column.name, column)
        self.assertEqual(actual, struct_type)

    def test_transform_invalid_array_inner_type(self) -> None:
        column = ColumnMetadata("col1", None, "array<array<int*>>", 0)
        column.set_column_key(self.column_key)

        with self.assertRaises(ParseException):
            parse_event_bridge_type(column.type, column.name, column)

    def test_transform_valid_only_type_struct(self) -> None:
        column = ColumnMetadata("col1", None, "struct<object>", 0)
        column.set_column_key(self.column_key)

        struct_type = StructTypeMetadata(
            name="col1", parent=column, type_str="struct<object>"
        )
        inner_scalar_nest1 = ScalarTypeMetadata(
            name="value", parent=struct_type, type_str="object"
        )

        struct_type.struct_items = {
            "value": inner_scalar_nest1,
        }
        inner_scalar_nest1.sort_order = 0

        actual = parse_event_bridge_type(column.type, column.name, column)
        self.assertEqual(actual, struct_type)

    def test_transform_invalid_struct_inner_type(self) -> None:
        column = ColumnMetadata(
            "col1",
            None,
            "struct<nest1:varchar(256)å," "nest2:<derived from deserializer>>",
            0,
        )
        column.set_column_key(self.column_key)

        with self.assertRaises(ParseException):
            parse_event_bridge_type(column.type, column.name, column)


if __name__ == "__main__":
    unittest.main()
