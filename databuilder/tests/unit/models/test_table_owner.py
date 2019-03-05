import unittest
from databuilder.models.user import User
from databuilder.models.table_owner import TableOwner


from databuilder.models.neo4j_csv_serde import RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


db = 'hive'
SCHEMA = 'BASE'
TABLE = 'TEST'
CLUSTER = 'DEFAULT'


class TestTableOwner(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        super(TestTableOwner, self).setUp()
        self.table_owner = TableOwner(db_name='hive',
                                      schema_name=SCHEMA,
                                      table_name=TABLE,
                                      cluster=CLUSTER,
                                      owners=['user1@1', 'user2@2'])

    def test_get_owner_model_key(self):
        # type: () -> None
        owner = self.table_owner.get_owner_model_key('user1@1')
        self.assertEquals(owner, 'user1@1')

    def test_get_metadata_model_key(self):
        # type: () -> None
        metadata = self.table_owner.get_metadata_model_key()
        self.assertEquals(metadata, 'hive://default.base/test')

    def test_create_nodes(self):
        # type: () -> None
        nodes = self.table_owner.create_nodes()
        self.assertEquals(len(nodes), 2)

    def test_create_relation(self):
        # type: () -> None
        relations = self.table_owner.create_relation()
        self.assertEquals(len(relations), 2)

        relation = {
            RELATION_START_KEY: 'user1@1',
            RELATION_START_LABEL: User.USER_NODE_LABEL,
            RELATION_END_KEY: self.table_owner.get_metadata_model_key(),
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: TableOwner.OWNER_TABLE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableOwner.TABLE_OWNER_RELATION_TYPE
        }

        self.assertTrue(relation in relations)
