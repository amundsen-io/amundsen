# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.table_lineage import TableLineage
from databuilder.models.neo4j_csv_serde import RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


DB = 'hive'
SCHEMA = 'base'
TABLE = 'test'
CLUSTER = 'default'


class TestTableLineage(unittest.TestCase):

    def setUp(self) -> None:
        super(TestTableLineage, self).setUp()
        self.table_lineage = TableLineage(db_name='hive',
                                          schema=SCHEMA,
                                          table_name=TABLE,
                                          cluster=CLUSTER,
                                          downstream_deps=['hive://default.test_schema/test_table1',
                                                           'hive://default.test_schema/test_table2'])

    def test_get_table_model_key(self) -> None:
        metadata = self.table_lineage.get_table_model_key(db=DB,
                                                          cluster=CLUSTER,
                                                          schema=SCHEMA,
                                                          table=TABLE)
        self.assertEquals(metadata, 'hive://default.base/test')

    def test_create_nodes(self) -> None:
        nodes = self.table_lineage.create_nodes()
        self.assertEquals(len(nodes), 0)

    def test_create_relation(self) -> None:
        relations = self.table_lineage.create_relation()
        self.assertEquals(len(relations), 2)

        start_key = '{db}://{cluster}.{schema}/{tbl}'.format(db=DB,
                                                             schema=SCHEMA,
                                                             tbl=TABLE,
                                                             cluster=CLUSTER)
        end_key1 = '{db}://{cluster}.{schema}/{tbl}'.format(db=DB,
                                                            schema='test_schema',
                                                            tbl='test_table1',
                                                            cluster=CLUSTER)

        relation = {
            RELATION_START_KEY: start_key,
            RELATION_START_LABEL: 'Table',
            RELATION_END_KEY: end_key1,
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: TableLineage.ORIGIN_DEPENDENCY_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableLineage.DEPENDENCY_ORIGIN_RELATION_TYPE
        }
        self.assertTrue(len(relations), 2)
        self.assertTrue(relation in relations)
