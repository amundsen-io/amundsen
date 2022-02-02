# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.table_metadata import ColumnMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata,
    MapTypeMetadata,
    StructItem,
    StructTypeMetadata,
    TypeMetadata,
)
from databuilder.serializers import neo4_serializer


class TestTypeMetadata(unittest.TestCase):
    def test_serialize_array_type_metadata(self) -> None:
        nested_array_type_metadata_level2 = ArrayTypeMetadata(
            data_type='string',
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col1/array/array'
        )
        nested_array_type_metadata_level1 = ArrayTypeMetadata(
            data_type=nested_array_type_metadata_level2,
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col1/array'
        )
        array_type_metadata = ArrayTypeMetadata(
            data_type=nested_array_type_metadata_level1,
            start_label=ColumnMetadata.COLUMN_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col1'
        )

        expected_nodes = [
            {'kind': 'array', 'LABEL': 'Column_Subtype',
             'data_type': 'array<array<string>>',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/array'},
            {'kind': 'array', 'LABEL': 'Column_Subtype',
             'data_type': 'array<string>',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/array/array'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/array',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY':
             'hive://gold.test_schema1/test_table1/col1/array/array',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/array',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'}
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
        nested_array_type_metadata_level2 = ArrayTypeMetadata(
            data_type='string',
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col1/array/map'
        )
        nested_map_type_metadata_level1 = MapTypeMetadata(
            key='string',
            value=nested_array_type_metadata_level2,
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col1/array'
        )
        array_type_metadata = ArrayTypeMetadata(
            data_type=nested_map_type_metadata_level1,
            start_label=ColumnMetadata.COLUMN_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col1'
        )

        expected_nodes = [
            {'kind': 'array', 'data_type': 'map<string,array<string>>',
             'LABEL': 'Column_Subtype',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/array'},
            {'kind': 'map', 'map_key': 'string',
             'map_value': 'array<string>', 'LABEL': 'Column_Subtype',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/array/map'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/array',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/array/map',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/array',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'}
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
        nested_array_type_metadata_level2 = ArrayTypeMetadata(
            data_type='string',
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col1/array/c1'
        )
        nested_struct_type_metadata_level1 = StructTypeMetadata(
            struct_items=[
                StructItem(name='c1',
                           description=None,
                           data_type=nested_array_type_metadata_level2),
                StructItem(name='c2',
                           description=None,
                           data_type='string')
            ],
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col1/array'
        )
        array_type_metadata = ArrayTypeMetadata(
            data_type=nested_struct_type_metadata_level1,
            start_label=ColumnMetadata.COLUMN_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col1'
        )

        expected_nodes = [
            {'kind': 'array', 'data_type': 'struct<c1:array<string>,c2:string>',
             'LABEL': 'Column_Subtype',
             'KEY': 'hive://gold.test_schema1/test_table1/col1/array'},
            {'kind': 'struct', 'name': 'c1', 'data_type': 'array<string>',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/array/c1'},
            {'kind': 'struct', 'name': 'c2', 'data_type': 'string',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col1/array/c2'},
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/array',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/array/c1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/array',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col1/array/c2',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col1/array',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'}
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
        nested_map_type_metadata_level2 = MapTypeMetadata(
            key='string',
            value='string',
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col2/map/map'
        )
        nested_map_type_metadata_level1 = MapTypeMetadata(
            key='string',
            value=nested_map_type_metadata_level2,
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col2/map'
        )
        map_type_metadata = MapTypeMetadata(
            key='string',
            value=nested_map_type_metadata_level1,
            start_label=ColumnMetadata.COLUMN_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col2'
        )

        expected_nodes = [
            {'kind': 'map', 'map_key': 'string',
             'map_value': 'map<string,map<string,string>>',
             'LABEL': 'Column_Subtype',
             'KEY': 'hive://gold.test_schema1/test_table1/col2/map'},
            {'kind': 'map', 'map_key': 'string',
             'map_value': 'map<string,string>', 'LABEL': 'Column_Subtype',
             'KEY': 'hive://gold.test_schema1/test_table1/col2/map/map'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col2/map',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col2',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col2/map/map',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col2/map',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'}
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
        nested_map_type_metadata_level2 = MapTypeMetadata(
            key='string',
            value='string',
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col2/map/c1'
        )
        nested_struct_type_metadata_level1 = StructTypeMetadata(
            struct_items=[
                StructItem(name='c1',
                           description=None,
                           data_type=nested_map_type_metadata_level2),
                StructItem(name='c2',
                           description=None,
                           data_type='string')
            ],
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col2/map'
        )
        map_type_metadata = MapTypeMetadata(
            key='string',
            value=nested_struct_type_metadata_level1,
            start_label=ColumnMetadata.COLUMN_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col2'
        )

        expected_nodes = [
            {'kind': 'map', 'map_key': 'string',
             'map_value': 'struct<c1:map<string,string>,c2:string>',
             'LABEL': 'Column_Subtype',
             'KEY': 'hive://gold.test_schema1/test_table1/col2/map'},
            {'kind': 'struct', 'name': 'c1', 'data_type': 'map<string,string>',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col2/map/c1'},
            {'kind': 'struct', 'name': 'c2', 'data_type': 'string',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col2/map/c2'},
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col2/map',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col2',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col2/map/c1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col2/map',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col2/map/c2',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col2/map',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'}
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
        nested_struct_type_metadata_level2 = StructTypeMetadata(
            struct_items=[
                StructItem(name='c3',
                           description='description of c3',
                           data_type='string'),
                StructItem(name='c4',
                           description=None,
                           data_type='string')
            ],
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col3/c1/c2'
        )
        nested_struct_type_metadata_level1 = StructTypeMetadata(
            struct_items=[
                StructItem(name='c2',
                           description=None,
                           data_type=nested_struct_type_metadata_level2)
            ],
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col3/c1'
        )
        struct_type_metadata = StructTypeMetadata(
            struct_items=[
                StructItem(name='c1',
                           description=None,
                           data_type=nested_struct_type_metadata_level1),
                StructItem(name='c5',
                           description='description of c5',
                           data_type='string')
            ],
            start_label=ColumnMetadata.COLUMN_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col3'
        )

        expected_nodes = [
            {'kind': 'struct', 'name': 'c1',
             'data_type': 'struct<c2:struct<c3:string,c4:string>>',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col3/c1'},
            {'kind': 'struct', 'name': 'c2',
             'data_type': 'struct<c3:string,c4:string>',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col3/c1/c2'},
            {'kind': 'struct', 'name': 'c3', 'data_type': 'string',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col3/c1/c2/c3'},
            {'description': 'description of c3',
             'KEY':
             'hive://gold.test_schema1/test_table1/col3/c1/c2/c3/_description',
             'LABEL': 'Description', 'description_source': 'description'},
            {'kind': 'struct', 'name': 'c4', 'data_type': 'string',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col3/c1/c2/c4'},
            {'kind': 'struct', 'name': 'c5', 'data_type': 'string',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col3/c5'},
            {'description': 'description of c5',
             'KEY':
             'hive://gold.test_schema1/test_table1/col3/c5/_description',
             'LABEL': 'Description', 'description_source': 'description'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col3/c1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col3/c1/c2',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3/c1',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col3/c1/c2/c3',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3/c1/c2',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY':
             'hive://gold.test_schema1/test_table1/col3/c1/c2/c3/_description',
             'START_LABEL': 'Column_Subtype', 'END_LABEL': 'Description',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3/c1/c2/c3',
             'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col3/c1/c2/c4',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3/c1/c2',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column_Subtype',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col3/c5',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY':
             'hive://gold.test_schema1/test_table1/col3/c5/_description',
             'START_LABEL': 'Column_Subtype', 'END_LABEL': 'Description',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3/c5',
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
        nested_array_type_metadata_level2 = ArrayTypeMetadata(
            data_type='string',
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col3/c1/map'
        )
        nested_array_type_metadata_level1 = ArrayTypeMetadata(
            data_type='string',
            start_label=TypeMetadata.TYPE_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col3/c2'
        )
        nested_map_type_metadata_level1 = MapTypeMetadata(
            key='string',
            value=nested_array_type_metadata_level2,
            start_label=ColumnMetadata.COLUMN_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col3/c1'
        )
        struct_type_metadata = StructTypeMetadata(
            struct_items=[
                StructItem(name='c1',
                           description=None,
                           data_type=nested_map_type_metadata_level1),
                StructItem(name='c2',
                           description=None,
                           data_type=nested_array_type_metadata_level1)
            ],
            start_label=ColumnMetadata.COLUMN_NODE_LABEL,
            start_key='hive://gold.test_schema1/test_table1/col3'
        )

        expected_nodes = [
            {'kind': 'struct', 'name': 'c1',
             'data_type': 'map<string,array<string>>',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 0,
             'KEY': 'hive://gold.test_schema1/test_table1/col3/c1'},
            {'kind': 'map', 'map_key': 'string',
             'map_value': 'array<string>', 'LABEL': 'Column_Subtype',
             'KEY': 'hive://gold.test_schema1/test_table1/col3/c1/map'},
            {'kind': 'struct', 'name': 'c2',
             'data_type': 'array<string>',
             'LABEL': 'Column_Subtype', 'sort_order:UNQUOTED': 1,
             'KEY': 'hive://gold.test_schema1/test_table1/col3/c2'}
        ]
        expected_rels = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col3/c1',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col3/c1/map',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3/c1',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/col3/c2',
             'START_KEY': 'hive://gold.test_schema1/test_table1/col3',
             'END_LABEL': 'Column_Subtype', 'START_LABEL': 'Column',
             'TYPE': 'COLUMN_SUBTYPE', 'REVERSE_TYPE': 'COLUMN_SUBTYPE_OF'}
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
