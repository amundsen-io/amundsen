# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import ANY

from databuilder.models.schema.schema import SchemaModel
from databuilder.serializers import neo4_serializer, neptune_serializer
from databuilder.serializers.neptune_serializer import (
    NEPTUNE_CREATION_TYPE_JOB, NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT,
    NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_HEADER_ID, NEPTUNE_HEADER_LABEL,
    NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_RELATIONSHIP_HEADER_FROM,
    NEPTUNE_RELATIONSHIP_HEADER_TO,
)


class TestSchemaDescription(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = SchemaModel(
            schema_key='db://cluster.schema',
            schema='schema_name',
            description='foo'
        )

    def test_create_nodes(self) -> None:
        schema_node = self.schema.create_next_node()
        serialized_schema_node = neo4_serializer.serialize_node(schema_node)
        schema_desc_node = self.schema.create_next_node()
        serialized_schema_desc_node = neo4_serializer.serialize_node(schema_desc_node)
        self.assertDictEqual(
            serialized_schema_node,
            {'name': 'schema_name', 'KEY': 'db://cluster.schema', 'LABEL': 'Schema'}
        )
        self.assertDictEqual(serialized_schema_desc_node,
                             {'description_source': 'description', 'description': 'foo',
                              'KEY': 'db://cluster.schema/_description', 'LABEL': 'Description'}
                             )
        self.assertIsNone(self.schema.create_next_node())

    def test_create_nodes_neptune(self) -> None:
        schema_node = self.schema.create_next_node()
        expected_serialized_schema_node = {
            NEPTUNE_HEADER_ID: 'db://cluster.schema',
            NEPTUNE_HEADER_LABEL: 'Schema',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            'name:String(single)': 'schema_name',
        }
        serialized_schema_node = neptune_serializer.convert_node(schema_node)
        self.assertDictEqual(
            expected_serialized_schema_node,
            serialized_schema_node
        )
        schema_desc_node = self.schema.create_next_node()
        excepted_serialized_schema_desc_node = {
            NEPTUNE_HEADER_ID: 'db://cluster.schema/_description',
            NEPTUNE_HEADER_LABEL: 'Description',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            'description_source:String(single)': 'description',
            'description:String(single)': 'foo',
        }
        serialized_schema_desc_node = neptune_serializer.convert_node(schema_desc_node)
        self.assertDictEqual(
            excepted_serialized_schema_desc_node,
            serialized_schema_desc_node
        )

    def test_create_nodes_no_description(self) -> None:

        schema = SchemaModel(schema_key='db://cluster.schema',
                             schema='schema_name')

        schema_node = schema.create_next_node()
        serialized_schema_node = neo4_serializer.serialize_node(schema_node)

        self.assertDictEqual(serialized_schema_node,
                             {'name': 'schema_name', 'KEY': 'db://cluster.schema', 'LABEL': 'Schema'})
        self.assertIsNone(schema.create_next_node())

    def test_create_nodes_programmatic_description(self) -> None:

        schema = SchemaModel(schema_key='db://cluster.schema',
                             schema='schema_name',
                             description='foo',
                             description_source='bar')

        schema_node = schema.create_next_node()
        serialized_schema_node = neo4_serializer.serialize_node(schema_node)
        schema_desc_node = schema.create_next_node()
        serialized_schema_prod_desc_node = neo4_serializer.serialize_node(schema_desc_node)

        self.assertDictEqual(serialized_schema_node,
                             {'name': 'schema_name', 'KEY': 'db://cluster.schema', 'LABEL': 'Schema'})
        self.assertDictEqual(serialized_schema_prod_desc_node,
                             {'description_source': 'bar', 'description': 'foo',
                              'KEY': 'db://cluster.schema/_bar_description', 'LABEL': 'Programmatic_Description'})
        self.assertIsNone(schema.create_next_node())

    def test_create_relation(self) -> None:
        actual = self.schema.create_next_relation()
        serialized_actual = neo4_serializer.serialize_relationship(actual)
        expected = {'END_KEY': 'db://cluster.schema/_description', 'START_LABEL': 'Schema', 'END_LABEL': 'Description',
                    'START_KEY': 'db://cluster.schema', 'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'}

        self.assertEqual(expected, serialized_actual)
        self.assertIsNone(self.schema.create_next_relation())

    def test_create_relation_neptune(self) -> None:
        actual = self.schema.create_next_relation()
        serialized_actual = neptune_serializer.convert_relationship(actual)

        neptune_forward_expected = {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='db://cluster.schema',
                to_vertex_id='db://cluster.schema/_description',
                label='DESCRIPTION'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'db://cluster.schema',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'db://cluster.schema/_description',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }

        neptune_reversed_expected = {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='db://cluster.schema/_description',
                to_vertex_id='db://cluster.schema',
                label='DESCRIPTION_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'db://cluster.schema/_description',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'db://cluster.schema',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }

        self.assertDictEqual(serialized_actual[0], neptune_forward_expected)
        self.assertDictEqual(serialized_actual[1], neptune_reversed_expected)

    def test_create_relation_no_description(self) -> None:
        schema = SchemaModel(schema_key='db://cluster.schema',
                             schema='schema_name')

        self.assertIsNone(schema.create_next_relation())

    def test_create_relation_programmatic_description(self) -> None:
        schema = SchemaModel(schema_key='db://cluster.schema',
                             schema='schema_name',
                             description='foo',
                             description_source='bar')

        actual = schema.create_next_relation()
        serialized_actual = neo4_serializer.serialize_relationship(actual)
        expected = {
            'END_KEY': 'db://cluster.schema/_bar_description', 'START_LABEL': 'Schema',
            'END_LABEL': 'Programmatic_Description', 'START_KEY': 'db://cluster.schema', 'TYPE': 'DESCRIPTION',
            'REVERSE_TYPE': 'DESCRIPTION_OF'
        }

        self.assertEqual(expected, serialized_actual)
        self.assertIsNone(schema.create_next_relation())
