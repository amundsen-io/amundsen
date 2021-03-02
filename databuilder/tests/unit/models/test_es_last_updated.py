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

        self.expected_node_results = [{
            NODE_KEY: 'amundsen_updated_timestamp',
            NODE_LABEL: 'Updatedtimestamp',
            'latest_timestamp:UNQUOTED': 100,
        }]

    def test_create_nodes(self) -> None:
        actual = []
        node = self.neo4j_es_last_updated.create_next_node()
        while node:
            serialized_node = neo4_serializer.serialize_node(node)
            actual.append(serialized_node)
            node = self.neo4j_es_last_updated.create_next_node()

        self.assertEqual(actual, self.expected_node_results)

    def test_create_next_relation(self) -> None:
        self.assertIs(self.neo4j_es_last_updated.create_next_relation(), None)
