# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.dashboard.dashboard_table import DashboardTable
from databuilder.models.neo4j_csv_serde import RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


class TestDashboardTable(unittest.TestCase):

    def test_dashboard_table_nodes(self):
        # type: () -> None
        dashboard_table = DashboardTable(table_ids=['hive://gold.schema/table1', 'hive://gold.schema/table2'],
                                         cluster='cluster_id', product='product_id',
                                         dashboard_id='dashboard_id', dashboard_group_id='dashboard_group_id')

        actual = dashboard_table.create_next_node()
        self.assertIsNone(actual)

    def test_dashboard_table_relations(self):
        # type: () -> None
        dashboard_table = DashboardTable(table_ids=['hive://gold.schema/table1'],
                                         cluster='cluster_id', product='product_id',
                                         dashboard_id='dashboard_id', dashboard_group_id='dashboard_group_id')

        actual = dashboard_table.create_next_relation()
        expected = {RELATION_END_KEY: 'hive://gold.schema/table1', RELATION_START_LABEL: 'Dashboard',
                    RELATION_END_LABEL: 'Table',
                    RELATION_START_KEY: 'product_id_dashboard://cluster_id.dashboard_group_id/dashboard_id',
                    RELATION_TYPE: 'DASHBOARD_WITH_TABLE',
                    RELATION_REVERSE_TYPE: 'TABLE_OF_DASHBOARD'}
        self.assertDictEqual(actual, expected)
