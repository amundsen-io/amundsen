# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from typing import Dict, List
from unittest.mock import ANY

from databuilder.models.badge import Badge, BadgeMetadata
from databuilder.models.graph_serializable import (
    NODE_KEY, NODE_LABEL, RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY,
    RELATION_START_LABEL, RELATION_TYPE,
)
from databuilder.serializers import neo4_serializer, neptune_serializer
from databuilder.serializers.neptune_serializer import (
    METADATA_KEY_PROPERTY_NAME, NEPTUNE_CREATION_TYPE_JOB, NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT,
    NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_HEADER_ID, NEPTUNE_HEADER_LABEL,
    NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_RELATIONSHIP_HEADER_FROM,
    NEPTUNE_RELATIONSHIP_HEADER_TO,
)

db = 'hive'
SCHEMA = 'BASE'
TABLE = 'TEST'
CLUSTER = 'DEFAULT'
badge1 = Badge('badge1', 'column')
badge2 = Badge('badge2', 'column')


class TestBadge(unittest.TestCase):
    def setUp(self) -> None:
        super(TestBadge, self).setUp()
        self.badge_metada = BadgeMetadata(start_label='Column',
                                          start_key='hive://default.base/test/ds',
                                          badges=[badge1, badge2])

    def test_get_badge_key(self) -> None:
        badge_key = self.badge_metada.get_badge_key(badge1.name)
        self.assertEqual(badge_key, badge1.name)

    def test_create_nodes(self) -> None:
        nodes = self.badge_metada.create_nodes()
        self.assertEqual(len(nodes), 2)

        node1 = {
            NODE_KEY: BadgeMetadata.BADGE_KEY_FORMAT.format(badge=badge1.name),
            NODE_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            BadgeMetadata.BADGE_CATEGORY: badge1.category
        }
        node2 = {
            NODE_KEY: BadgeMetadata.BADGE_KEY_FORMAT.format(badge=badge2.name),
            NODE_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            BadgeMetadata.BADGE_CATEGORY: badge2.category
        }
        serialized_nodes = [
            neo4_serializer.serialize_node(node)
            for node in nodes
        ]

        self.assertTrue(node1 in serialized_nodes)
        self.assertTrue(node2 in serialized_nodes)

    def test_create_nodes_neptune(self) -> None:
        nodes = self.badge_metada.create_nodes()
        serialized_nodes = [
            neptune_serializer.convert_node(node)
            for node in nodes
        ]
        node_id_1 = BadgeMetadata.BADGE_NODE_LABEL + ":" + BadgeMetadata.BADGE_KEY_FORMAT.format(badge=badge1.name)
        expected_node1 = {
            NEPTUNE_HEADER_ID: node_id_1,
            METADATA_KEY_PROPERTY_NAME: node_id_1,
            NEPTUNE_HEADER_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            BadgeMetadata.BADGE_CATEGORY + ':String(single)': badge1.category
        }
        node_id_2 = BadgeMetadata.BADGE_NODE_LABEL + ":" + BadgeMetadata.BADGE_KEY_FORMAT.format(badge=badge2.name)
        expected_node2 = {
            NEPTUNE_HEADER_ID: node_id_2,
            METADATA_KEY_PROPERTY_NAME: node_id_2,
            NEPTUNE_HEADER_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            BadgeMetadata.BADGE_CATEGORY + ':String(single)': badge2.category
        }

        self.assertTrue(expected_node1 in serialized_nodes)
        self.assertTrue(expected_node2 in serialized_nodes)

    def test_bad_key_entity_match(self) -> None:
        column_label = 'Column'
        table_key = 'hive://default.base/test'

        self.assertRaises(Exception,
                          BadgeMetadata,
                          start_label=column_label,
                          start_key=table_key,
                          badges=[badge1, badge2])

    def test_bad_entity_label(self) -> None:
        user_label = 'User'
        table_key = 'hive://default.base/test'
        self.assertRaises(Exception,
                          BadgeMetadata,
                          start_label=user_label,
                          start_key=table_key,
                          badges=[badge1, badge2])

    def test_create_relation(self) -> None:
        relations = self.badge_metada.create_relation()
        serialized_relations = [
            neo4_serializer.serialize_relationship(relation)
            for relation in relations
        ]
        self.assertEqual(len(relations), 2)

        relation1 = {
            RELATION_START_LABEL: self.badge_metada.start_label,
            RELATION_END_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            RELATION_START_KEY: self.badge_metada.start_key,
            RELATION_END_KEY: BadgeMetadata.get_badge_key(badge1.name),
            RELATION_TYPE: BadgeMetadata.BADGE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: BadgeMetadata.INVERSE_BADGE_RELATION_TYPE,
        }
        relation2 = {
            RELATION_START_LABEL: self.badge_metada.start_label,
            RELATION_END_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            RELATION_START_KEY: self.badge_metada.start_key,
            RELATION_END_KEY: BadgeMetadata.get_badge_key(badge2.name),
            RELATION_TYPE: BadgeMetadata.BADGE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: BadgeMetadata.INVERSE_BADGE_RELATION_TYPE,
        }

        self.assertTrue(relation1 in serialized_relations)
        self.assertTrue(relation2 in serialized_relations)

    def test_create_relation_neptune(self) -> None:
        relations = self.badge_metada.create_relation()
        serialized_relations: List[Dict] = sum([
            neptune_serializer.convert_relationship(rel) for rel in relations
        ], [])

        badge_id_1 = BadgeMetadata.BADGE_NODE_LABEL + ':' + BadgeMetadata.get_badge_key(badge1.name)
        badge_id_2 = BadgeMetadata.BADGE_NODE_LABEL + ':' + BadgeMetadata.get_badge_key(badge2.name)
        start_key = self.badge_metada.start_label + ':' + self.badge_metada.start_key

        neptune_forward_expected_1 = {
            NEPTUNE_HEADER_ID: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                from_vertex_id=start_key,
                to_vertex_id=badge_id_1,
                label=BadgeMetadata.BADGE_RELATION_TYPE,
            ),
            METADATA_KEY_PROPERTY_NAME: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                from_vertex_id=start_key,
                to_vertex_id=badge_id_1,
                label=BadgeMetadata.BADGE_RELATION_TYPE,
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: start_key,
            NEPTUNE_RELATIONSHIP_HEADER_TO: badge_id_1,
            NEPTUNE_HEADER_LABEL: BadgeMetadata.BADGE_RELATION_TYPE,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }

        neptune_reversed_expected_1 = {
            NEPTUNE_HEADER_ID: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                from_vertex_id=badge_id_1,
                to_vertex_id=start_key,
                label=BadgeMetadata.INVERSE_BADGE_RELATION_TYPE
            ),
            METADATA_KEY_PROPERTY_NAME: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                from_vertex_id=badge_id_1,
                to_vertex_id=start_key,
                label=BadgeMetadata.INVERSE_BADGE_RELATION_TYPE
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: badge_id_1,
            NEPTUNE_RELATIONSHIP_HEADER_TO: start_key,
            NEPTUNE_HEADER_LABEL: BadgeMetadata.INVERSE_BADGE_RELATION_TYPE,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }

        neptune_forward_expected_2 = {
            NEPTUNE_HEADER_ID: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                from_vertex_id=start_key,
                to_vertex_id=badge_id_2,
                label=BadgeMetadata.BADGE_RELATION_TYPE,
            ),
            METADATA_KEY_PROPERTY_NAME: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                from_vertex_id=start_key,
                to_vertex_id=badge_id_2,
                label=BadgeMetadata.BADGE_RELATION_TYPE,
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: start_key,
            NEPTUNE_RELATIONSHIP_HEADER_TO: badge_id_2,
            NEPTUNE_HEADER_LABEL: BadgeMetadata.BADGE_RELATION_TYPE,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }

        neptune_reversed_expected_2 = {
            NEPTUNE_HEADER_ID: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                from_vertex_id=badge_id_2,
                to_vertex_id=start_key,
                label=BadgeMetadata.INVERSE_BADGE_RELATION_TYPE,
            ),
            METADATA_KEY_PROPERTY_NAME: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                from_vertex_id=badge_id_2,
                to_vertex_id=start_key,
                label=BadgeMetadata.INVERSE_BADGE_RELATION_TYPE,
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: badge_id_2,
            NEPTUNE_RELATIONSHIP_HEADER_TO: start_key,
            NEPTUNE_HEADER_LABEL: BadgeMetadata.INVERSE_BADGE_RELATION_TYPE,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }

        self.assertTrue(neptune_forward_expected_1 in serialized_relations)
        self.assertTrue(neptune_reversed_expected_1 in serialized_relations)
        self.assertTrue(neptune_forward_expected_2 in serialized_relations)
        self.assertTrue(neptune_reversed_expected_2 in serialized_relations)
