# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.dashboard.dashboard_owner import DashboardOwner
from databuilder.models.neo4j_csv_serde import RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


class TestDashboardOwner(unittest.TestCase):

    def test_dashboard_owner_nodes(self) -> None:
        dashboard_owner = DashboardOwner(email='foo@bar.com', cluster='cluster_id', product='product_id',
                                         dashboard_id='dashboard_id', dashboard_group_id='dashboard_group_id')

        actual = dashboard_owner.create_next_node()
        self.assertIsNone(actual)

    def test_dashboard_owner_relations(self) -> None:
        dashboard_owner = DashboardOwner(email='foo@bar.com', cluster='cluster_id', product='product_id',
                                         dashboard_id='dashboard_id', dashboard_group_id='dashboard_group_id')

        actual = dashboard_owner.create_next_relation()
        expected = {RELATION_END_KEY: 'foo@bar.com', RELATION_START_LABEL: 'Dashboard', RELATION_END_LABEL: 'User',
                    RELATION_START_KEY: 'product_id_dashboard://cluster_id.dashboard_group_id/dashboard_id',
                    RELATION_TYPE: 'OWNER',
                    RELATION_REVERSE_TYPE: 'OWNER_OF'}
        assert actual is not None
        self.assertDictEqual(actual, expected)
