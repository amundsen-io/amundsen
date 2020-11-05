# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.table_lineage import TableLineage
from databuilder.models.graph_serializable import RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE
from databuilder.serializers import neo4_serializer


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
        self.assertEqual(metadata, 'hive://default.base/test')

    def test_create_nodes(self) -> None:
        nodes = self.table_lineage.create_nodes()
        self.assertEqual(len(nodes), 0)

    def test_create_relation(self) -> None:
        relations = self.table_lineage.create_relation()
        self.assertEqual(len(relations), 2)

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
        actual_relations = [
            neo4_serializer.serialize_relationship(relation)
            for relation in relations
        ]
        self.assertTrue(len(relations), 2)
        self.assertTrue(relation in actual_relations)
