# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.graph_serializable import (
    NODE_KEY, NODE_LABEL, RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY,
    RELATION_START_LABEL, RELATION_TYPE,
)
from databuilder.models.table_last_updated import TableLastUpdated
from databuilder.models.timestamp import timestamp_constants
from databuilder.serializers import neo4_serializer


class TestTableLastUpdated(unittest.TestCase):

    def setUp(self) -> None:
        super(TestTableLastUpdated, self).setUp()

        self.tableLastUpdated = TableLastUpdated(table_name='test_table',
                                                 last_updated_time_epoch=25195665,
                                                 schema='default')

        self.expected_node_result = {
            NODE_KEY: 'hive://gold.default/test_table/timestamp',
            NODE_LABEL: 'Timestamp',
            'last_updated_timestamp:UNQUOTED': 25195665,
            timestamp_constants.TIMESTAMP_PROPERTY + ":UNQUOTED": 25195665,
            'name': 'last_updated_timestamp'
        }

        self.expected_relation_result = {
            RELATION_START_KEY: 'hive://gold.default/test_table',
            RELATION_START_LABEL: 'Table',
            RELATION_END_KEY: 'hive://gold.default/test_table/timestamp',
            RELATION_END_LABEL: 'Timestamp',
            RELATION_TYPE: 'LAST_UPDATED_AT',
            RELATION_REVERSE_TYPE: 'LAST_UPDATED_TIME_OF'
        }

    def test_create_next_node(self) -> None:
        next_node = self.tableLastUpdated.create_next_node()
        next_node_serialized = neo4_serializer.serialize_node(next_node)
        self.assertEqual(next_node_serialized, self.expected_node_result)

    def test_create_next_relation(self) -> None:
        next_relation = self.tableLastUpdated.create_next_relation()
        next_relation_serialized = neo4_serializer.serialize_relationship(next_relation)
        self.assertEqual(next_relation_serialized, self.expected_relation_result)

    def test_get_table_model_key(self) -> None:
        table = self.tableLastUpdated.get_table_model_key()
        self.assertEqual(table, 'hive://gold.default/test_table')

    def test_get_last_updated_model_key(self) -> None:
        last_updated = self.tableLastUpdated.get_last_updated_model_key()
        self.assertEqual(last_updated, 'hive://gold.default/test_table/timestamp')

    def test_create_nodes(self) -> None:
        nodes = self.tableLastUpdated.create_nodes()
        self.assertEquals(len(nodes), 1)
        serialize_node = neo4_serializer.serialize_node(nodes[0])
        self.assertEquals(serialize_node, self.expected_node_result)

    def test_create_relation(self) -> None:
        relation = self.tableLastUpdated.create_relation()
        self.assertEquals(len(relation), 1)
        serialized_relation = neo4_serializer.serialize_relationship(relation[0])
        self.assertEquals(serialized_relation, self.expected_relation_result)
