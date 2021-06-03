# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.feature.feature_query import FeatureQuery
from databuilder.serializers import neo4_serializer


class TestFeatureQuery(unittest.TestCase):
    def setUp(self) -> None:
        self.basic_query = FeatureQuery(
            feature_group='group1',
            feature_name='feat_name_123',
            feature_version='2.0.0',
            text='select * from hive.schema.table',
            last_executed_timestamp=1622596581,
        )

        self.expected_nodes = [
            {
                'KEY': 'feature://group1/feat_name_123/2.0.0/_query',
                'LABEL': 'Feature_Query',
                'text': 'select * from hive.schema.table',
                'last_executed_timestamp:UNQUOTED': 1622596581,
            }
        ]

        self.expected_rels = [
            {
                'START_LABEL': 'Feature',
                'END_LABEL': 'Feature_Query',
                'START_KEY': 'feature://group1/feat_name_123/2.0.0',
                'END_KEY': 'feature://group1/feat_name_123/2.0.0/_query',
                'TYPE': 'HAS_QUERY',
                'REVERSE_TYPE': 'QUERY_OF',
            }
        ]

    def test_basic_example(self) -> None:
        node_row = self.basic_query.next_node()
        actual = []
        while node_row:
            node_serialized = neo4_serializer.serialize_node(node_row)
            actual.append(node_serialized)
            node_row = self.basic_query.next_node()

        self.assertEqual(self.expected_nodes, actual)

        relation_row = self.basic_query.next_relation()
        actual = []
        while relation_row:
            relation_serialized = neo4_serializer.serialize_relationship(relation_row)
            actual.append(relation_serialized)
            relation_row = self.basic_query.next_relation()
        self.assertEqual(self.expected_rels, actual)


if __name__ == '__main__':
    unittest.main()
