# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import ANY

from databuilder.models.graph_serializable import (
    NODE_KEY, NODE_LABEL, RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY,
    RELATION_START_LABEL, RELATION_TYPE,
)
from databuilder.models.table_stats import TableColumnStats
from databuilder.serializers import neo4_serializer, neptune_serializer
from databuilder.serializers.neptune_serializer import (
    NEPTUNE_CREATION_TYPE_JOB, NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT,
    NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_HEADER_ID, NEPTUNE_HEADER_LABEL,
    NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_RELATIONSHIP_HEADER_FROM,
    NEPTUNE_RELATIONSHIP_HEADER_TO,
)


class TestTableStats(unittest.TestCase):

    def setUp(self) -> None:
        super(TestTableStats, self).setUp()
        self.table_stats = TableColumnStats(table_name='base.test',
                                            col_name='col',
                                            stat_name='avg',
                                            stat_val='1',
                                            start_epoch='1',
                                            end_epoch='2',)

        self.expected_node_result = {
            NODE_KEY: 'hive://gold.base/test/col/avg/',
            NODE_LABEL: 'Stat',
            'stat_val': '1',
            'stat_name': 'avg',
            'start_epoch': '1',
            'end_epoch': '2',
        }

        self.expected_relation_result = {
            RELATION_START_KEY: 'hive://gold.base/test/col/avg/',
            RELATION_START_LABEL: 'Stat',
            RELATION_END_KEY: 'hive://gold.base/test/col',
            RELATION_END_LABEL: 'Column',
            RELATION_TYPE: 'STAT_OF',
            RELATION_REVERSE_TYPE: 'STAT'
        }

    def test_get_table_stat_model_key(self) -> None:
        table_stats = self.table_stats.get_table_stat_model_key()
        self.assertEqual(table_stats, 'hive://gold.base/test/col/avg/')

    def test_get_col_key(self) -> None:
        metadata = self.table_stats.get_col_key()
        self.assertEqual(metadata, 'hive://gold.base/test/col')

    def test_create_nodes(self) -> None:
        nodes = self.table_stats.create_nodes()
        self.assertEquals(len(nodes), 1)
        serialized_node = neo4_serializer.serialize_node(nodes[0])
        self.assertEquals(serialized_node, self.expected_node_result)

    def test_create_relation(self) -> None:
        relation = self.table_stats.create_relation()

        self.assertEquals(len(relation), 1)
        serialized_relation = neo4_serializer.serialize_relationship(relation[0])
        self.assertEquals(serialized_relation, self.expected_relation_result)

    def test_create_next_node(self) -> None:
        next_node = self.table_stats.create_next_node()
        serialized_node = neo4_serializer.serialize_node(next_node)
        self.assertEquals(serialized_node, self.expected_node_result)

    def test_create_next_node_neptune(self) -> None:
        next_node = self.table_stats.create_next_node()
        serialized_node = neptune_serializer.convert_node(next_node)
        expected_neptune_node = {
            NEPTUNE_HEADER_ID: 'hive://gold.base/test/col/avg/',
            NEPTUNE_HEADER_LABEL: 'Stat',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            'stat_val:String(single)': '1',
            'stat_name:String(single)': 'avg',
            'start_epoch:String(single)': '1',
            'end_epoch:String(single)': '2',
        }
        self.assertDictEqual(serialized_node, expected_neptune_node)

    def test_create_next_relation(self) -> None:
        next_relation = self.table_stats.create_next_relation()
        serialized_relation = neo4_serializer.serialize_relationship(next_relation)
        self.assertEquals(serialized_relation, self.expected_relation_result)

    def test_create_next_relation_neptune(self) -> None:
        next_relation = self.table_stats.create_next_relation()

        self.expected_relation_result = {
            RELATION_START_KEY: 'hive://gold.base/test/col/avg/',
            RELATION_START_LABEL: 'Stat',
            RELATION_END_KEY: 'hive://gold.base/test/col',
            RELATION_END_LABEL: 'Column',
            RELATION_TYPE: 'STAT_OF',
            RELATION_REVERSE_TYPE: 'STAT'
        }

        expected = [
            {
                NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                    from_vertex_id='hive://gold.base/test/col/avg/',
                    to_vertex_id='hive://gold.base/test/col',
                    label='STAT_OF'
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.base/test/col/avg/',
                NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.base/test/col',
                NEPTUNE_HEADER_LABEL: 'STAT_OF',
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
            },
            {
                NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                    from_vertex_id='hive://gold.base/test/col',
                    to_vertex_id='hive://gold.base/test/col/avg/',
                    label='STAT'
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.base/test/col',
                NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.base/test/col/avg/',
                NEPTUNE_HEADER_LABEL: 'STAT',
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
            }
        ]

        serialized_relation = neptune_serializer.convert_relationship(next_relation)
        self.assertListEqual(serialized_relation, expected)
