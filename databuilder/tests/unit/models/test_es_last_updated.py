# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.es_last_updated import ESLastUpdated
from databuilder.models.graph_serializable import NODE_KEY, NODE_LABEL
from databuilder.serializers import neo4_serializer


class TestNeo4jESLastUpdated(unittest.TestCase):

    def setUp(self) -> None:
        super(TestNeo4jESLastUpdated, self).setUp()
        self.neo4j_es_last_updated = ESLastUpdated(timestamp=100)

        self.expected_node_result = {
            NODE_KEY: 'amundsen_updated_timestamp',
            NODE_LABEL: 'Updatedtimestamp',
            'latest_timestmap:UNQUOTED': 100,
        }

    def test_create_nodes(self) -> None:
        nodes = self.neo4j_es_last_updated.create_nodes()
        self.assertEquals(len(nodes), 1)
        serialized_node = neo4_serializer.serialize_node(nodes[0])
        self.assertEquals(serialized_node, self.expected_node_result)

    def test_create_next_node(self) -> None:
        next_node = self.neo4j_es_last_updated.create_next_node()
        self.assertEquals(neo4_serializer.serialize_node(next_node), self.expected_node_result)

    def test_create_next_relation(self) -> None:
        self.assertIs(self.neo4j_es_last_updated.create_next_relation(), None)
