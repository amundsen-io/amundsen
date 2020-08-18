# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from databuilder.models.user import User
from databuilder.models.table_owner import TableOwner


from databuilder.models.neo4j_csv_serde import NODE_KEY, NODE_LABEL, \
    RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


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
                                      owners="user1@1, UsER2@2 ")

    def test_get_owner_model_key(self) -> None:
        owner = self.table_owner.get_owner_model_key(owner1)
        self.assertEquals(owner, owner1)

    def test_get_metadata_model_key(self) -> None:
        metadata = self.table_owner.get_metadata_model_key()
        self.assertEquals(metadata, 'hive://default.base/test')

    def test_create_nodes(self) -> None:
        nodes = self.table_owner.create_nodes()
        self.assertEquals(len(nodes), 2)

        node1 = {
            NODE_KEY: User.USER_NODE_KEY_FORMAT.format(email=owner1),
            NODE_LABEL: User.USER_NODE_LABEL,
            User.USER_NODE_EMAIL: owner1
        }
        node2 = {
            NODE_KEY: User.USER_NODE_KEY_FORMAT.format(email=owner2),
            NODE_LABEL: User.USER_NODE_LABEL,
            User.USER_NODE_EMAIL: owner2
        }

        self.assertTrue(node1 in nodes)
        self.assertTrue(node2 in nodes)

    def test_create_relation(self) -> None:
        relations = self.table_owner.create_relation()
        self.assertEquals(len(relations), 2)

        relation1 = {
            RELATION_START_KEY: owner1,
            RELATION_START_LABEL: User.USER_NODE_LABEL,
            RELATION_END_KEY: self.table_owner.get_metadata_model_key(),
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: TableOwner.OWNER_TABLE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableOwner.TABLE_OWNER_RELATION_TYPE
        }
        relation2 = {
            RELATION_START_KEY: owner2,
            RELATION_START_LABEL: User.USER_NODE_LABEL,
            RELATION_END_KEY: self.table_owner.get_metadata_model_key(),
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: TableOwner.OWNER_TABLE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableOwner.TABLE_OWNER_RELATION_TYPE
        }

        self.assertTrue(relation1 in relations)
        self.assertTrue(relation2 in relations)

    def test_create_nodes_with_owners_list(self) -> None:
        self.table_owner_list = TableOwner(db_name='hive',
                                           schema=SCHEMA,
                                           table_name=TABLE,
                                           cluster=CLUSTER,
                                           owners=['user1@1', ' UsER2@2 '])
        nodes = self.table_owner_list.create_nodes()
        self.assertEquals(len(nodes), 2)

        node1 = {
            NODE_KEY: User.USER_NODE_KEY_FORMAT.format(email=owner1),
            NODE_LABEL: User.USER_NODE_LABEL,
            User.USER_NODE_EMAIL: owner1
        }
        node2 = {
            NODE_KEY: User.USER_NODE_KEY_FORMAT.format(email=owner2),
            NODE_LABEL: User.USER_NODE_LABEL,
            User.USER_NODE_EMAIL: owner2
        }

        self.assertTrue(node1 in nodes)
        self.assertTrue(node2 in nodes)
