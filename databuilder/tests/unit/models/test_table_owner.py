# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import ANY

from databuilder.models.graph_serializable import (
    NODE_KEY, NODE_LABEL, RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY,
    RELATION_START_LABEL, RELATION_TYPE,
)
from databuilder.models.table_owner import TableOwner
from databuilder.models.user import User
from databuilder.serializers import neo4_serializer, neptune_serializer
from databuilder.serializers.neptune_serializer import (
    NEPTUNE_CREATION_TYPE_JOB, NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT,
    NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_HEADER_ID, NEPTUNE_HEADER_LABEL,
    NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_RELATIONSHIP_HEADER_FROM,
    NEPTUNE_RELATIONSHIP_HEADER_TO,
)

db = 'hive'
SCHEMA = 'BASE'
TABLE = 'TEST'
CLUSTER = 'DEFAULT'
owner1 = 'user1@1'
owner2 = 'user2@2'


class TestTableOwner(unittest.TestCase):

    def setUp(self) -> None:
        super(TestTableOwner, self).setUp()
        self.table_owner = TableOwner(db_name='hive',
                                      schema=SCHEMA,
                                      table_name=TABLE,
                                      cluster=CLUSTER,
                                      owners="user1@1, user2@2 ")

    def test_get_owner_model_key(self) -> None:
        owner = self.table_owner.get_owner_model_key(owner1)
        self.assertEqual(owner, owner1)

    def test_get_metadata_model_key(self) -> None:
        metadata = self.table_owner.get_metadata_model_key()
        self.assertEqual(metadata, 'hive://DEFAULT.BASE/TEST')

    def test_create_nodes(self) -> None:
        nodes = self.table_owner.create_nodes()
        self.assertEqual(len(nodes), 2)

        expected_node1 = {
            NODE_KEY: User.USER_NODE_KEY_FORMAT.format(email=owner1),
            NODE_LABEL: User.USER_NODE_LABEL,
            User.USER_NODE_EMAIL: owner1
        }
        expected_node2 = {
            NODE_KEY: User.USER_NODE_KEY_FORMAT.format(email=owner2),
            NODE_LABEL: User.USER_NODE_LABEL,
            User.USER_NODE_EMAIL: owner2
        }
        actual_nodes = [
            neo4_serializer.serialize_node(node)
            for node in nodes
        ]

        self.assertTrue(expected_node1 in actual_nodes)
        self.assertTrue(expected_node2 in actual_nodes)

    def test_create_nodes_neptune(self) -> None:
        nodes = self.table_owner.create_nodes()

        expected_node1 = {
            NEPTUNE_HEADER_ID: User.USER_NODE_KEY_FORMAT.format(email=owner1),
            NEPTUNE_HEADER_LABEL: User.USER_NODE_LABEL,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            User.USER_NODE_EMAIL + ":String(single)": owner1
        }
        expected_node2 = {
            NEPTUNE_HEADER_ID: User.USER_NODE_KEY_FORMAT.format(email=owner2),
            NEPTUNE_HEADER_LABEL: User.USER_NODE_LABEL,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            User.USER_NODE_EMAIL + ":String(single)": owner2
        }

        actual_nodes = [
            neptune_serializer.convert_node(node)
            for node in nodes
        ]

        self.assertTrue(expected_node1 in actual_nodes)
        self.assertTrue(expected_node2 in actual_nodes)

    def test_create_relation(self) -> None:
        relations = self.table_owner.create_relation()
        self.assertEqual(len(relations), 2)

        expected_relation1 = {
            RELATION_START_KEY: owner1,
            RELATION_START_LABEL: User.USER_NODE_LABEL,
            RELATION_END_KEY: self.table_owner.get_metadata_model_key(),
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: TableOwner.OWNER_TABLE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableOwner.TABLE_OWNER_RELATION_TYPE
        }
        expected_relation2 = {
            RELATION_START_KEY: owner2,
            RELATION_START_LABEL: User.USER_NODE_LABEL,
            RELATION_END_KEY: self.table_owner.get_metadata_model_key(),
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: TableOwner.OWNER_TABLE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableOwner.TABLE_OWNER_RELATION_TYPE
        }

        actual_relations = [
            neo4_serializer.serialize_relationship(relation)
            for relation in relations
        ]

        self.assertTrue(expected_relation1 in actual_relations)
        self.assertTrue(expected_relation2 in actual_relations)

    def test_create_relation_neptune(self) -> None:
        relations = self.table_owner.create_relation()
        expected = [
            {
                NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                    from_vertex_id=owner1,
                    to_vertex_id=self.table_owner.get_metadata_model_key(),
                    label=TableOwner.OWNER_TABLE_RELATION_TYPE
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: owner1,
                NEPTUNE_RELATIONSHIP_HEADER_TO: self.table_owner.get_metadata_model_key(),
                NEPTUNE_HEADER_LABEL: TableOwner.OWNER_TABLE_RELATION_TYPE,
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
            },
            {
                NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                    from_vertex_id=self.table_owner.get_metadata_model_key(),
                    to_vertex_id=owner1,
                    label=TableOwner.TABLE_OWNER_RELATION_TYPE
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: self.table_owner.get_metadata_model_key(),
                NEPTUNE_RELATIONSHIP_HEADER_TO: owner1,
                NEPTUNE_HEADER_LABEL: TableOwner.TABLE_OWNER_RELATION_TYPE,
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
            }
        ]

        actual_relations = [
            neptune_serializer.convert_relationship(relation)
            for relation in relations
        ]
        self.assertTrue(expected in actual_relations)

    def test_create_nodes_with_owners_list(self) -> None:
        self.table_owner_list = TableOwner(db_name='hive',
                                           schema=SCHEMA,
                                           table_name=TABLE,
                                           cluster=CLUSTER,
                                           owners=['user1@1', ' user2@2 '])
        nodes = self.table_owner_list.create_nodes()
        self.assertEqual(len(nodes), 2)

        expected_node1 = {
            NODE_KEY: User.USER_NODE_KEY_FORMAT.format(email=owner1),
            NODE_LABEL: User.USER_NODE_LABEL,
            User.USER_NODE_EMAIL: owner1
        }
        expected_node2 = {
            NODE_KEY: User.USER_NODE_KEY_FORMAT.format(email=owner2),
            NODE_LABEL: User.USER_NODE_LABEL,
            User.USER_NODE_EMAIL: owner2
        }
        actual_nodes = [
            neo4_serializer.serialize_node(node)
            for node in nodes
        ]

        self.assertTrue(expected_node1 in actual_nodes)
        self.assertTrue(expected_node2 in actual_nodes)
