# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from databuilder.models.user import User
from databuilder.models.table_owner import TableOwner


from databuilder.models.graph_serializable import NODE_KEY, NODE_LABEL, \
    RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE
from databuilder.serializers import neo4_serializer


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
