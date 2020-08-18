# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from databuilder.models.neo4j_es_last_updated import Neo4jESLastUpdated

from databuilder.models.neo4j_csv_serde import NODE_KEY, \
    NODE_LABEL


class TestNeo4jESLastUpdated(unittest.TestCase):

    def setUp(self) -> None:
        super(TestNeo4jESLastUpdated, self).setUp()
        self.neo4j_es_last_updated = Neo4jESLastUpdated(timestamp=100)

        self.expected_node_result = {
            NODE_KEY: 'amundsen_updated_timestamp',
            NODE_LABEL: 'Updatedtimestamp',
            'latest_timestmap': 100,
        }

    def test_create_nodes(self) -> None:
        nodes = self.neo4j_es_last_updated.create_nodes()
        self.assertEquals(len(nodes), 1)
        self.assertEquals(nodes[0], self.expected_node_result)

    def test_create_next_node(self) -> None:
        next_node = self.neo4j_es_last_updated.create_next_node()
        self.assertEquals(next_node, self.expected_node_result)

    def test_create_next_relation(self) -> None:
        self.assertIs(self.neo4j_es_last_updated.create_next_relation(), None)
