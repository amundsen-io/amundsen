# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from databuilder.models.table_stats import TableColumnStats

from databuilder.models.neo4j_csv_serde import NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


class TestTableStats(unittest.TestCase):

    def setUp(self) -> None:
        super(TestTableStats, self).setUp()
        self.table_stats = TableColumnStats(table_name='base.test',
                                            col_name='col',
                                            stat_name='avg',
                                            stat_val='1',
                                            start_epoch='1',
                                            end_epoch='2',)

        self.expected_node_result = {
            NODE_KEY: 'hive://gold.base/test/col/avg/',
            NODE_LABEL: 'Stat',
            'stat_val:UNQUOTED': '1',
            'stat_name': 'avg',
            'start_epoch': '1',
            'end_epoch': '2',
        }

        self.expected_relation_result = {
            RELATION_START_KEY: 'hive://gold.base/test/col/avg/',
            RELATION_START_LABEL: 'Stat',
            RELATION_END_KEY: 'hive://gold.base/test/col',
            RELATION_END_LABEL: 'Column',
            RELATION_TYPE: 'STAT_OF',
            RELATION_REVERSE_TYPE: 'STAT'
        }

    def test_get_table_stat_model_key(self) -> None:
        table_stats = self.table_stats.get_table_stat_model_key()
        self.assertEquals(table_stats, 'hive://gold.base/test/col/avg/')

    def test_get_col_key(self) -> None:
        metadata = self.table_stats.get_col_key()
        self.assertEquals(metadata, 'hive://gold.base/test/col')

    def test_create_nodes(self) -> None:
        nodes = self.table_stats.create_nodes()
        self.assertEquals(len(nodes), 1)
        self.assertEquals(nodes[0], self.expected_node_result)

    def test_create_relation(self) -> None:
        relation = self.table_stats.create_relation()
        self.assertEquals(len(relation), 1)
        self.assertEquals(relation[0], self.expected_relation_result)

    def test_create_next_node(self) -> None:
        next_node = self.table_stats.create_next_node()
        self.assertEquals(next_node, self.expected_node_result)

    def test_create_next_relation(self) -> None:
        next_relation = self.table_stats.create_next_relation()
        self.assertEquals(next_relation, self.expected_relation_result)
