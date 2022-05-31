# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.table_metadata import ColumnMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata, MapTypeMetadata, ScalarTypeMetadata, StructTypeMetadata,
)
from databuilder.serializers import neo4_serializer


class TestTypeMetadata(unittest.TestCase):
    def setUp(self) -> None:
        self.column_key = 'hive://gold.test_schema1/test_table1/col1'

    def test_serialize_array_type_metadata(self) -> None:
        column = ColumnMetadata('col1', None, 'array<array<array<string>>>', 0)
        column.set_column_key(self.column_key)

        array_type_metadata = ArrayTypeMetadata(
            name='col1',
            parent=column,
            type_str='array<array<array<string>>>'
        )
        nested_array_type_metadata_level1 = ArrayTypeMetadata(
            name='_inner_',
            parent=array_type_metadata,
            type_str='array<array<string>>'
        )
        nested_array_type_metadata_level2 = ArrayTypeMetadata(
            name='_inner_',
            parent=nested_array_type_metadata_level1,
            type_str='array<string>'
        )
        nested_scalar_type_metadata_level3 = ScalarTypeMetadata(
            name='_inner_',
            parent=nested_array_type_metadata_level2,
            type_str='string'
        )

        array_type_metadata.array_inner_type = nested_array_type_metadata_level1
        nested_array_type_metadata_level1.array_inner_type = nested_array_type_metadata_level2
        nested_array_type_metadata_level2.array_inner_type = nested_scalar_type_metadata_level3

        expected_nodes = [
            {'kind': 'array', 'name': 'col1', 'LABEL': 'Type_Metadata', 'data_type': 'array<array<array<string>>>',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1'},
            {'kind': 'array', 'name': '_inner_', 'LABEL': 'Type_Metadata', 'data_type': 'array<array<string>>',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_'},
            {'kind': 'array', 'name': '_inner_', 'LABEL': 'Type_Metadata', 'data_type': 'array<string>',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/_inner_'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Column',
             'TYPE': 'TYPE_METADATA', 'REVERSE_TYPE': 'TYPE_METADATA_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/_inner_',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'}
        ]

        node_row = array_type_metadata.next_node()
        actual = []
        while node_row:
            node_row_serialized = neo4_serializer.serialize_node(node_row)
            actual.append(node_row_serialized)
            node_row = array_type_metadata.next_node()
        for i in range(0, len(expected_nodes)):
            self.assertEqual(actual[i], expected_nodes[i])

        relation_row = array_type_metadata.next_relation()
        actual = []
        while relation_row:
            relation_row_serialized = neo4_serializer.serialize_relationship(
                relation_row
            )
            actual.append(relation_row_serialized)
            relation_row = array_type_metadata.next_relation()
        for i in range(0, len(expected_rels)):
            self.assertEqual(actual[i], expected_rels[i])

    def test_serialize_array_map_type_metadata(self) -> None:
        column = ColumnMetadata('col1', None, 'array<map<string,array<string>>>', 0)
        column.set_column_key(self.column_key)

        array_type_metadata = ArrayTypeMetadata(
            name='col1',
            parent=column,
            type_str='array<map<string,array<string>>>'
        )
        nested_map_type_metadata_level1 = MapTypeMetadata(
            name='_inner_',
            parent=array_type_metadata,
            type_str='map<string,array<string>>'
        )
        nested_map_key = ScalarTypeMetadata(
            name='_map_key',
            parent=nested_map_type_metadata_level1,
            type_str='string'
        )
        nested_array_type_metadata_level2 = ArrayTypeMetadata(
            name='_map_value',
            parent=nested_map_type_metadata_level1,
            type_str='array<string>'
        )
        nested_scalar_type_metadata_level3 = ScalarTypeMetadata(
            name='_inner_',
            parent=nested_array_type_metadata_level2,
            type_str='string'
        )

        array_type_metadata.array_inner_type = nested_map_type_metadata_level1
        nested_map_type_metadata_level1.map_key_type = nested_map_key
        nested_map_type_metadata_level1.map_value_type = nested_array_type_metadata_level2
        nested_array_type_metadata_level2.array_inner_type = nested_scalar_type_metadata_level3

        expected_nodes = [
            {'kind': 'array', 'data_type': 'array<map<string,array<string>>>',
             'LABEL': 'Type_Metadata', 'name': 'col1',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1'},
            {'kind': 'map', 'data_type': 'map<string,array<string>>', 'LABEL': 'Type_Metadata', 'name': '_inner_',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_'},
            {'kind': 'scalar', 'data_type': 'string', 'LABEL': 'Type_Metadata', 'name': '_map_key',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/_map_key'},
            {'kind': 'array', 'data_type': 'array<string>', 'LABEL': 'Type_Metadata', 'name': '_map_value',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/_map_value'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Column',
             'TYPE': 'TYPE_METADATA', 'REVERSE_TYPE': 'TYPE_METADATA_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/_map_key',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/_map_value',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'}
        ]

        node_row = array_type_metadata.next_node()
        actual = []
        while node_row:
            node_row_serialized = neo4_serializer.serialize_node(node_row)
            actual.append(node_row_serialized)
            node_row = array_type_metadata.next_node()
        for i in range(0, len(expected_nodes)):
            self.assertEqual(actual[i], expected_nodes[i])

        relation_row = array_type_metadata.next_relation()
        actual = []
        while relation_row:
            relation_row_serialized = neo4_serializer.serialize_relationship(
                relation_row
            )
            actual.append(relation_row_serialized)
            relation_row = array_type_metadata.next_relation()
        for i in range(0, len(expected_rels)):
            self.assertEqual(actual[i], expected_rels[i])

    def test_serialize_array_struct_type_metadata(self) -> None:
        column = ColumnMetadata('col1', None, 'array<struct<c1:array<string>,c2:string>>', 0)
        column.set_column_key(self.column_key)

        array_type_metadata = ArrayTypeMetadata(
            name='col1',
            parent=column,
            type_str='array<struct<c1:array<string>,c2:string>>'
        )
        nested_struct_type_metadata_level1 = StructTypeMetadata(
            name='_inner_',
            parent=array_type_metadata,
            type_str='struct<c1:array<string>,c2:string>'
        )
        nested_array_type_metadata_level2 = ArrayTypeMetadata(
            name='c1',
            parent=nested_struct_type_metadata_level1,
            type_str='array<string>'
        )
        nested_scalar_type_metadata_level2 = ScalarTypeMetadata(
            name='c2',
            parent=nested_struct_type_metadata_level1,
            type_str='string'
        )

        array_type_metadata.array_inner_type = nested_struct_type_metadata_level1
        nested_struct_type_metadata_level1.struct_items = {'c1': nested_array_type_metadata_level2,
                                                           'c2': nested_scalar_type_metadata_level2}
        nested_array_type_metadata_level2.sort_order = 0
        nested_scalar_type_metadata_level2.sort_order = 1

        expected_nodes = [
            {'kind': 'array', 'name': 'col1', 'data_type': 'array<struct<c1:array<string>,c2:string>>',
             'LABEL': 'Type_Metadata', 'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1'},
            {'kind': 'struct', 'name': '_inner_', 'data_type': 'struct<c1:array<string>,c2:string>',
             'LABEL': 'Type_Metadata', 'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_'},
            {'kind': 'array', 'name': 'c1', 'data_type': 'array<string>',
             'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/c1'},
            {'kind': 'scalar', 'name': 'c2', 'data_type': 'string',
             'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/c2'},
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Column',
             'TYPE': 'TYPE_METADATA', 'REVERSE_TYPE': 'TYPE_METADATA_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/c1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_/c2',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_inner_',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'}
        ]

        node_row = array_type_metadata.next_node()
        actual = []
        while node_row:
            node_row_serialized = neo4_serializer.serialize_node(node_row)
            actual.append(node_row_serialized)
            node_row = array_type_metadata.next_node()
        for i in range(0, len(expected_nodes)):
            self.assertEqual(actual[i], expected_nodes[i])

        relation_row = array_type_metadata.next_relation()
        actual = []
        while relation_row:
            relation_row_serialized = neo4_serializer.serialize_relationship(
                relation_row
            )
            actual.append(relation_row_serialized)
            relation_row = array_type_metadata.next_relation()
        for i in range(0, len(expected_rels)):
            self.assertEqual(actual[i], expected_rels[i])

    def test_serialize_map_type_metadata(self) -> None:
        column = ColumnMetadata('col1', None, 'map<string,map<string,map<string,string>>>', 0)
        column.set_column_key(self.column_key)

        map_type_metadata = MapTypeMetadata(
            name='col1',
            parent=column,
            type_str='map<string,map<string,map<string,string>>>'
        )
        map_key = ScalarTypeMetadata(
            name='_map_key',
            parent=map_type_metadata,
            type_str='string'
        )
        nested_map_type_metadata_level1 = MapTypeMetadata(
            name='_map_value',
            parent=map_type_metadata,
            type_str='map<string,map<string,string>>'
        )
        nested_map_key_level1 = ScalarTypeMetadata(
            name='_map_key',
            parent=nested_map_type_metadata_level1,
            type_str='string'
        )
        nested_map_type_metadata_level2 = MapTypeMetadata(
            name='_map_value',
            parent=nested_map_type_metadata_level1,
            type_str='map<string,string>'
        )
        nested_map_key_level2 = ScalarTypeMetadata(
            name='_map_key',
            parent=nested_map_type_metadata_level2,
            type_str='string'
        )
        nested_scalar_type_metadata_level3 = ScalarTypeMetadata(
            name='_map_value',
            parent=nested_map_type_metadata_level2,
            type_str='string'
        )

        map_type_metadata.map_key_type = map_key
        map_type_metadata.map_value_type = nested_map_type_metadata_level1
        nested_map_type_metadata_level1.map_key_type = nested_map_key_level1
        nested_map_type_metadata_level1.map_value_type = nested_map_type_metadata_level2
        nested_map_type_metadata_level2.map_key_type = nested_map_key_level2
        nested_map_type_metadata_level2.map_value_type = nested_scalar_type_metadata_level3

        expected_nodes = [
            {'kind': 'map', 'name': 'col1', 'data_type': 'map<string,map<string,map<string,string>>>',
             'LABEL': 'Type_Metadata', 'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1'},
            {'kind': 'scalar', 'name': '_map_key', 'data_type': 'string', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_key'},
            {'kind': 'map', 'name': '_map_value', 'data_type': 'map<string,map<string,string>>',
             'LABEL': 'Type_Metadata', 'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value'},
            {'kind': 'scalar', 'name': '_map_key', 'data_type': 'string', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/_map_key'},
            {'kind': 'map', 'name': '_map_value', 'data_type': 'map<string,string>', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/_map_value'},
            {'kind': 'scalar', 'name': '_map_key', 'data_type': 'string', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/_map_value/_map_key'},
            {'kind': 'scalar', 'name': '_map_value', 'data_type': 'string', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/_map_value/_map_value'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1', 'END_LABEL': 'Type_Metadata',
             'START_LABEL': 'Column', 'TYPE': 'TYPE_METADATA', 'REVERSE_TYPE': 'TYPE_METADATA_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_key',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1', 'END_LABEL': 'Type_Metadata',
             'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1', 'END_LABEL': 'Type_Metadata',
             'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/_map_key',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE',
             'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/_map_value',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE',
             'REVERSE_TYPE': 'SUBTYPE_OF'}
        ]

        node_row = map_type_metadata.next_node()
        actual = []
        while node_row:
            node_row_serialized = neo4_serializer.serialize_node(node_row)
            actual.append(node_row_serialized)
            node_row = map_type_metadata.next_node()
        for i in range(0, len(expected_nodes)):
            self.assertEqual(actual[i], expected_nodes[i])

        relation_row = map_type_metadata.next_relation()
        actual = []
        while relation_row:
            relation_row_serialized = neo4_serializer.serialize_relationship(
                relation_row
            )
            actual.append(relation_row_serialized)
            relation_row = map_type_metadata.next_relation()
        for i in range(0, len(expected_rels)):
            self.assertEqual(actual[i], expected_rels[i])

    def test_serialize_map_struct_type_metadata(self) -> None:
        column = ColumnMetadata('col1', None, 'map<string,struct<c1:map<string,string>,c2:string>>', 0)
        column.set_column_key(self.column_key)

        map_type_metadata = MapTypeMetadata(
            name='col1',
            parent=column,
            type_str='map<string,struct<c1:map<string,string>,c2:string>>'
        )
        map_key = ScalarTypeMetadata(
            name='_map_key',
            parent=map_type_metadata,
            type_str='string'
        )
        nested_struct_type_metadata_level1 = StructTypeMetadata(
            name='_map_value',
            parent=map_type_metadata,
            type_str='struct<c1:map<string,string>,c2:string>'
        )
        nested_map_type_metadata_level2 = MapTypeMetadata(
            name='c1',
            parent=nested_struct_type_metadata_level1,
            type_str='map<string,string>'
        )
        nested_map_key = ScalarTypeMetadata(
            name='_map_key',
            parent=nested_map_type_metadata_level2,
            type_str='string'
        )
        nested_scalar_type_metadata_level3 = ScalarTypeMetadata(
            name='_map_value',
            parent=nested_map_type_metadata_level2,
            type_str='string'
        )
        nested_scalar_type_metadata_level2 = ScalarTypeMetadata(
            name='c2',
            parent=nested_struct_type_metadata_level1,
            type_str='string'
        )

        map_type_metadata.map_key_type = map_key
        map_type_metadata.map_value_type = nested_struct_type_metadata_level1
        nested_struct_type_metadata_level1.struct_items = {'c1': nested_map_type_metadata_level2,
                                                           'c2': nested_scalar_type_metadata_level2}
        nested_map_type_metadata_level2.map_key_type = nested_map_key
        nested_map_type_metadata_level2.map_value_type = nested_scalar_type_metadata_level3
        nested_map_type_metadata_level2.sort_order = 0
        nested_scalar_type_metadata_level2.sort_order = 1

        expected_nodes = [
            {'kind': 'map', 'name': 'col1', 'data_type': 'map<string,struct<c1:map<string,string>,c2:string>>',
             'LABEL': 'Type_Metadata', 'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1'},
            {'kind': 'scalar', 'name': '_map_key', 'data_type': 'string', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_key'},
            {'kind': 'struct', 'name': '_map_value', 'data_type': 'struct<c1:map<string,string>,c2:string>',
             'LABEL': 'Type_Metadata', 'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value'},
            {'kind': 'map', 'name': 'c1', 'data_type': 'map<string,string>', 'sort_order:UNQUOTED': 0,
             'LABEL': 'Type_Metadata', 'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c1'},
            {'kind': 'scalar', 'name': '_map_key', 'data_type': 'string', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c1/_map_key'},
            {'kind': 'scalar', 'name': '_map_value', 'data_type': 'string', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c1/_map_value'},
            {'kind': 'scalar', 'name': 'c2', 'data_type': 'string', 'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c2'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1', 'END_LABEL': 'Type_Metadata',
             'START_LABEL': 'Column', 'TYPE': 'TYPE_METADATA', 'REVERSE_TYPE': 'TYPE_METADATA_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_key',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1', 'END_LABEL': 'Type_Metadata',
             'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1', 'END_LABEL': 'Type_Metadata',
             'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE',
             'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c1/_map_key',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE',
             'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c1/_map_value',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE',
             'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value/c2',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/_map_value',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata', 'TYPE': 'SUBTYPE',
             'REVERSE_TYPE': 'SUBTYPE_OF'}
        ]

        node_row = map_type_metadata.next_node()
        actual = []
        while node_row:
            node_row_serialized = neo4_serializer.serialize_node(node_row)
            actual.append(node_row_serialized)
            node_row = map_type_metadata.next_node()
        for i in range(0, len(expected_nodes)):
            self.assertEqual(actual[i], expected_nodes[i])

        relation_row = map_type_metadata.next_relation()
        actual = []
        while relation_row:
            relation_row_serialized = neo4_serializer.serialize_relationship(
                relation_row
            )
            actual.append(relation_row_serialized)
            relation_row = map_type_metadata.next_relation()
        for i in range(0, len(expected_rels)):
            self.assertEqual(actual[i], expected_rels[i])

    def test_serialize_struct_type_metadata(self) -> None:
        column = ColumnMetadata('col1', None, 'struct<c1:struct<c2:struct<c3:string,c4:string>>,c5:string>', 0)
        column.set_column_key(self.column_key)

        struct_type_metadata = StructTypeMetadata(
            name='col1',
            parent=column,
            type_str='struct<c1:struct<c2:struct<c3:string,c4:string>>,c5:string>'
        )
        nested_struct_type_metadata_level1 = StructTypeMetadata(
            name='c1',
            parent=struct_type_metadata,
            type_str='struct<c2:struct<c3:string,c4:string>>'
        )
        nested_struct_type_metadata_level2 = StructTypeMetadata(
            name='c2',
            parent=nested_struct_type_metadata_level1,
            type_str='struct<c3:string,c4:string>'
        )
        nested_scalar_type_metadata_c3 = ScalarTypeMetadata(
            name='c3',
            parent=nested_struct_type_metadata_level2,
            type_str='string',
            description='description of c3'
        )
        nested_scalar_type_metadata_c4 = ScalarTypeMetadata(
            name='c4',
            parent=nested_struct_type_metadata_level2,
            type_str='string'
        )
        nested_scalar_type_metadata_c5 = ScalarTypeMetadata(
            name='c5',
            parent=struct_type_metadata,
            type_str='string',
            description='description of c5'
        )

        struct_type_metadata.struct_items = {'c1': nested_struct_type_metadata_level1,
                                             'c5': nested_scalar_type_metadata_c5}
        nested_struct_type_metadata_level1.struct_items = {'c2': nested_struct_type_metadata_level2}
        nested_struct_type_metadata_level2.struct_items = {'c3': nested_scalar_type_metadata_c3,
                                                           'c4': nested_scalar_type_metadata_c4}
        nested_struct_type_metadata_level1.sort_order = 0
        nested_scalar_type_metadata_c5.sort_order = 1
        nested_struct_type_metadata_level2.sort_order = 0
        nested_scalar_type_metadata_c3.sort_order = 0
        nested_scalar_type_metadata_c4.sort_order = 1

        expected_nodes = [
            {'kind': 'struct', 'name': 'col1',
             'data_type': 'struct<c1:struct<c2:struct<c3:string,c4:string>>,c5:string>',
             'LABEL': 'Type_Metadata', 'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1'},
            {'kind': 'struct', 'name': 'c1', 'data_type': 'struct<c2:struct<c3:string,c4:string>>',
             'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1'},
            {'kind': 'struct', 'name': 'c2', 'data_type': 'struct<c3:string,c4:string>',
             'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2'},
            {'kind': 'scalar', 'name': 'c3', 'data_type': 'string',
             'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2/c3'},
            {'description': 'description of c3',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2/c3/_description',
             'LABEL': 'Description', 'description_source': 'description'},
            {'kind': 'scalar', 'name': 'c4', 'data_type': 'string',
             'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2/c4'},
            {'kind': 'scalar', 'name': 'c5', 'data_type': 'string',
             'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c5'},
            {'description': 'description of c5',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c5/_description',
             'LABEL': 'Description', 'description_source': 'description'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Column',
             'TYPE': 'TYPE_METADATA', 'REVERSE_TYPE': 'TYPE_METADATA_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2/c3',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2/c3/_description',
             'START_LABEL': 'Type_Metadata', 'END_LABEL': 'Description',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2/c3',
             'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2/c4',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/c2',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c5',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c5/_description',
             'START_LABEL': 'Type_Metadata', 'END_LABEL': 'Description',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c5',
             'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'}
        ]

        node_row = struct_type_metadata.next_node()
        actual = []
        while node_row:
            node_row_serialized = neo4_serializer.serialize_node(node_row)
            actual.append(node_row_serialized)
            node_row = struct_type_metadata.next_node()
        for i in range(0, len(expected_nodes)):
            self.assertEqual(actual[i], expected_nodes[i])

        relation_row = struct_type_metadata.next_relation()
        actual = []
        while relation_row:
            relation_row_serialized = neo4_serializer.serialize_relationship(
                relation_row
            )
            actual.append(relation_row_serialized)
            relation_row = struct_type_metadata.next_relation()
        for i in range(0, len(expected_rels)):
            self.assertEqual(actual[i], expected_rels[i])

    def test_serialize_struct_map_array_type_metadata(self) -> None:
        column = ColumnMetadata('col1', None, 'struct<c1:map<string,array<string>>,c2:array<string>>', 0)
        column.set_column_key(self.column_key)

        struct_type_metadata = StructTypeMetadata(
            name='col1',
            parent=column,
            type_str='struct<c1:map<string,array<string>>,c2:array<string>>'
        )
        nested_map_type_metadata_level1 = MapTypeMetadata(
            name='c1',
            parent=struct_type_metadata,
            type_str='map<string,array<string>>',
            description='description of map'
        )
        nested_map_key = ScalarTypeMetadata(
            name='_map_key',
            parent=nested_map_type_metadata_level1,
            type_str='string'
        )
        nested_array_type_metadata_level2 = ArrayTypeMetadata(
            name='_map_value',
            parent=nested_map_type_metadata_level1,
            type_str='array<string>'
        )
        nested_array_type_metadata_level1 = ArrayTypeMetadata(
            name='c2',
            parent=struct_type_metadata,
            type_str='array<string>',
            description='description of array'
        )

        struct_type_metadata.struct_items = {'c1': nested_map_type_metadata_level1,
                                             'c2': nested_array_type_metadata_level1}
        nested_map_type_metadata_level1.map_key_type = nested_map_key
        nested_map_type_metadata_level1.map_value_type = nested_array_type_metadata_level2
        nested_map_type_metadata_level1.sort_order = 0
        nested_array_type_metadata_level1.sort_order = 1

        expected_nodes = [
            {'kind': 'struct', 'name': 'col1', 'LABEL': 'Type_Metadata',
             'data_type': 'struct<c1:map<string,array<string>>,c2:array<string>>',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1'},
            {'kind': 'map', 'name': 'c1', 'data_type': 'map<string,array<string>>',
             'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1'},
            {'description': 'description of map',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/_description',
             'LABEL': 'Description', 'description_source': 'description'},
            {'kind': 'scalar', 'name': '_map_key',
             'data_type': 'string', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/_map_key'},
            {'kind': 'array', 'name': '_map_value',
             'data_type': 'array<string>', 'LABEL': 'Type_Metadata',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/_map_value'},
            {'kind': 'array', 'name': 'c2', 'data_type': 'array<string>',
             'LABEL': 'Type_Metadata', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c2'},
            {'description': 'description of array',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c2/_description',
             'LABEL': 'Description', 'description_source': 'description'},
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Column',
             'TYPE': 'TYPE_METADATA', 'REVERSE_TYPE': 'TYPE_METADATA_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/_description',
             'START_LABEL': 'Type_Metadata', 'END_LABEL': 'Description',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1',
             'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/_map_key',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1/_map_value',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c2',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1',
             'END_LABEL': 'Type_Metadata', 'START_LABEL': 'Type_Metadata',
             'TYPE': 'SUBTYPE', 'REVERSE_TYPE': 'SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c2/_description',
             'START_LABEL': 'Type_Metadata', 'END_LABEL': 'Description',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/type/col1/c2',
             'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'},
        ]

        node_row = struct_type_metadata.next_node()
        actual = []
        while node_row:
            node_row_serialized = neo4_serializer.serialize_node(node_row)
            actual.append(node_row_serialized)
            node_row = struct_type_metadata.next_node()
        for i in range(0, len(expected_nodes)):
            self.assertEqual(actual[i], expected_nodes[i])

        relation_row = struct_type_metadata.next_relation()
        actual = []
        while relation_row:
            relation_row_serialized = neo4_serializer.serialize_relationship(
                relation_row
            )
            actual.append(relation_row_serialized)
            relation_row = struct_type_metadata.next_relation()
        for i in range(0, len(expected_rels)):
            self.assertEqual(actual[i], expected_rels[i])


if __name__ == '__main__':
    unittest.main()
