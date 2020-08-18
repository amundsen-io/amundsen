# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.schema.schema import SchemaModel


class TestSchemaDescription(unittest.TestCase):

    def test_create_nodes(self) -> None:

        schema = SchemaModel(schema_key='db://cluster.schema',
                             schema='schema_name',
                             description='foo')

        self.assertDictEqual(schema.create_next_node() or {},
                             {'name': 'schema_name', 'KEY': 'db://cluster.schema', 'LABEL': 'Schema'})
        self.assertDictEqual(schema.create_next_node() or {},
                             {'description_source': 'description', 'description': 'foo',
                              'KEY': 'db://cluster.schema/_description', 'LABEL': 'Description'})
        self.assertIsNone(schema.create_next_node())

    def test_create_nodes_no_description(self) -> None:

        schema = SchemaModel(schema_key='db://cluster.schema',
                             schema='schema_name')

        self.assertDictEqual(schema.create_next_node() or {},
                             {'name': 'schema_name', 'KEY': 'db://cluster.schema', 'LABEL': 'Schema'})
        self.assertIsNone(schema.create_next_node())

    def test_create_nodes_programmatic_description(self) -> None:

        schema = SchemaModel(schema_key='db://cluster.schema',
                             schema='schema_name',
                             description='foo',
                             description_source='bar')

        self.assertDictEqual(schema.create_next_node() or {},
                             {'name': 'schema_name', 'KEY': 'db://cluster.schema', 'LABEL': 'Schema'})
        self.assertDictEqual(schema.create_next_node() or {},
                             {'description_source': 'bar', 'description': 'foo',
                              'KEY': 'db://cluster.schema/_bar_description', 'LABEL': 'Programmatic_Description'})
        self.assertIsNone(schema.create_next_node())

    def test_create_relation(self) -> None:
        schema = SchemaModel(schema_key='db://cluster.schema',
                             schema='schema_name',
                             description='foo')

        actual = schema.create_next_relation()
        expected = {'END_KEY': 'db://cluster.schema/_description', 'START_LABEL': 'Schema', 'END_LABEL': 'Description',
                    'START_KEY': 'db://cluster.schema', 'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'}

        self.assertEqual(expected, actual)
        self.assertIsNone(schema.create_next_relation())

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
        expected = {
            'END_KEY': 'db://cluster.schema/_bar_description', 'START_LABEL': 'Schema',
            'END_LABEL': 'Programmatic_Description', 'START_KEY': 'db://cluster.schema', 'TYPE': 'DESCRIPTION',
            'REVERSE_TYPE': 'DESCRIPTION_OF'
        }

        self.assertEqual(expected, actual)
        self.assertIsNone(schema.create_next_relation())
