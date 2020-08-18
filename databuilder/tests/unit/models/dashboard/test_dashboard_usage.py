# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from typing import Any, Dict

from databuilder.models.dashboard.dashboard_usage import DashboardUsage
from databuilder.models.neo4j_csv_serde import RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


class TestDashboardOwner(unittest.TestCase):

    def test_dashboard_usage_user_nodes(self) -> None:
        dashboard_usage = DashboardUsage(dashboard_group_id='dashboard_group_id', dashboard_id='dashboard_id',
                                         email='foo@bar.com', view_count=123, cluster='cluster_id',
                                         product='product_id', should_create_user_node=True)

        actual = dashboard_usage.create_next_node()
        expected: Dict[str, Any] = {
            'is_active:UNQUOTED': True,
            'last_name': '',
            'full_name': '',
            'employee_type': '',
            'first_name': '',
            'updated_at': 0,
            'LABEL': 'User',
            'slack_id': '',
            'KEY': 'foo@bar.com',
            'github_username': '',
            'team_name': '',
            'email': 'foo@bar.com',
            'role_name': ''
        }

        assert actual is not None
        self.assertDictEqual(expected, actual)
        self.assertIsNone(dashboard_usage.create_next_node())

    def test_dashboard_usage_no_user_nodes(self) -> None:
        dashboard_usage = DashboardUsage(dashboard_group_id='dashboard_group_id', dashboard_id='dashboard_id',
                                         email='foo@bar.com', view_count=123,
                                         should_create_user_node=False, cluster='cluster_id',
                                         product='product_id')

        self.assertIsNone(dashboard_usage.create_next_node())

    def test_dashboard_owner_relations(self) -> None:
        dashboard_usage = DashboardUsage(dashboard_group_id='dashboard_group_id', dashboard_id='dashboard_id',
                                         email='foo@bar.com', view_count=123, cluster='cluster_id',
                                         product='product_id')

        actual = dashboard_usage.create_next_relation()
        expected: Dict[str, Any] = {
            'read_count:UNQUOTED': 123,
            RELATION_END_KEY: 'foo@bar.com',
            RELATION_START_LABEL: 'Dashboard',
            RELATION_END_LABEL: 'User',
            RELATION_START_KEY: 'product_id_dashboard://cluster_id.dashboard_group_id/dashboard_id',
            RELATION_TYPE: 'READ_BY',
            RELATION_REVERSE_TYPE: 'READ'
        }

        assert actual is not None
        self.assertDictEqual(expected, actual)
        self.assertIsNone(dashboard_usage.create_next_relation())
