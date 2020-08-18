# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.table_source import TableSource
from databuilder.models.neo4j_csv_serde import RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


DB = 'hive'
SCHEMA = 'base'
TABLE = 'test'
CLUSTER = 'default'
SOURCE = '/etl/sql/file.py'


class TestTableSource(unittest.TestCase):

    def setUp(self) -> None:
        super(TestTableSource, self).setUp()
        self.table_source = TableSource(db_name='hive',
                                        schema=SCHEMA,
                                        table_name=TABLE,
                                        cluster=CLUSTER,
                                        source=SOURCE)

    def test_get_source_model_key(self) -> None:
        source = self.table_source.get_source_model_key()
        self.assertEquals(source, '{db}://{cluster}.{schema}/{tbl}/_source'.format(db=DB,
                                                                                   schema=SCHEMA,
                                                                                   tbl=TABLE,
                                                                                   cluster=CLUSTER,
                                                                                   ))

    def test_get_metadata_model_key(self) -> None:
        metadata = self.table_source.get_metadata_model_key()
        self.assertEquals(metadata, 'hive://default.base/test')

    def test_create_nodes(self) -> None:
        nodes = self.table_source.create_nodes()
        self.assertEquals(len(nodes), 1)

    def test_create_relation(self) -> None:
        relations = self.table_source.create_relation()
        self.assertEquals(len(relations), 1)

        start_key = '{db}://{cluster}.{schema}/{tbl}/_source'.format(db=DB,
                                                                     schema=SCHEMA,
                                                                     tbl=TABLE,
                                                                     cluster=CLUSTER)
        end_key = '{db}://{cluster}.{schema}/{tbl}'.format(db=DB,
                                                           schema=SCHEMA,
                                                           tbl=TABLE,
                                                           cluster=CLUSTER)

        relation = {
            RELATION_START_KEY: start_key,
            RELATION_START_LABEL: TableSource.LABEL,
            RELATION_END_KEY: end_key,
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: TableSource.SOURCE_TABLE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableSource.TABLE_SOURCE_RELATION_TYPE
        }

        self.assertTrue(relation in relations)
