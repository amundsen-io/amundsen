# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.dashboard.dashboard_table import DashboardTable
from databuilder.models.graph_serializable import (
    RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY, RELATION_START_LABEL,
    RELATION_TYPE,
)
from databuilder.serializers import neo4_serializer


class TestDashboardTable(unittest.TestCase):

    def test_dashboard_table_nodes(self) -> None:
        dashboard_table = DashboardTable(table_ids=['hive://gold.schema/table1', 'hive://gold.schema/table2'],
                                         cluster='cluster_id', product='product_id',
                                         dashboard_id='dashboard_id', dashboard_group_id='dashboard_group_id')

        actual = dashboard_table.create_next_node()
        self.assertIsNone(actual)

    def test_dashboard_table_relations(self) -> None:
        dashboard_table = DashboardTable(table_ids=['hive://gold.schema/table1'],
                                         cluster='cluster_id', product='product_id',
                                         dashboard_id='dashboard_id', dashboard_group_id='dashboard_group_id')

        actual = dashboard_table.create_next_relation()
        actual_serialized = neo4_serializer.serialize_relationship(actual)
        expected = {RELATION_END_KEY: 'hive://gold.schema/table1', RELATION_START_LABEL: 'Dashboard',
                    RELATION_END_LABEL: 'Table',
                    RELATION_START_KEY: 'product_id_dashboard://cluster_id.dashboard_group_id/dashboard_id',
                    RELATION_TYPE: 'DASHBOARD_WITH_TABLE',
                    RELATION_REVERSE_TYPE: 'TABLE_OF_DASHBOARD'}
        assert actual is not None
        self.assertDictEqual(actual_serialized, expected)

    def test_dashboard_table_without_dot_as_name(self) -> None:
        dashboard_table = DashboardTable(table_ids=['bq-name://project-id.schema-name/table-name'],
                                         cluster='cluster_id', product='product_id',
                                         dashboard_id='dashboard_id', dashboard_group_id='dashboard_group_id')
        actual = dashboard_table.create_next_relation()
        actual_serialized = neo4_serializer.serialize_relationship(actual)
        expected = {RELATION_END_KEY: 'bq-name://project-id.schema-name/table-name', RELATION_START_LABEL: 'Dashboard',
                    RELATION_END_LABEL: 'Table',
                    RELATION_START_KEY: 'product_id_dashboard://cluster_id.dashboard_group_id/dashboard_id',
                    RELATION_TYPE: 'DASHBOARD_WITH_TABLE',
                    RELATION_REVERSE_TYPE: 'TABLE_OF_DASHBOARD'}
        assert actual is not None
        self.assertDictEqual(actual_serialized, expected)

    def test_dashboard_table_with_dot_as_name(self) -> None:
        dashboard_table = DashboardTable(table_ids=['bq-name://project.id.schema-name/table-name'],
                                         cluster='cluster_id', product='product_id',
                                         dashboard_id='dashboard_id', dashboard_group_id='dashboard_group_id')
        actual = dashboard_table.create_next_relation()
        self.assertIsNone(actual)

    def test_dashboard_table_with_slash_as_name(self) -> None:
        dashboard_table = DashboardTable(table_ids=['bq/name://project/id.schema/name/table/name'],
                                         cluster='cluster_id', product='product_id',
                                         dashboard_id='dashboard_id', dashboard_group_id='dashboard_group_id')
        actual = dashboard_table.create_next_relation()
        self.assertIsNone(actual)
