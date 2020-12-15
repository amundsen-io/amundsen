# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from typing import Any, Dict

from databuilder.models.dashboard.dashboard_last_modified import DashboardLastModifiedTimestamp
from databuilder.models.graph_serializable import (
    RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY, RELATION_START_LABEL,
    RELATION_TYPE,
)
from databuilder.serializers import neo4_serializer


class TestDashboardLastModifiedTimestamp(unittest.TestCase):

    def test_dashboard_timestamp_nodes(self) -> None:
        dashboard_last_modified = DashboardLastModifiedTimestamp(last_modified_timestamp=123456789,
                                                                 cluster='cluster_id',
                                                                 product='product_id',
                                                                 dashboard_id='dashboard_id',
                                                                 dashboard_group_id='dashboard_group_id')

        actual = dashboard_last_modified.create_next_node()
        actual_serialized = neo4_serializer.serialize_node(actual)
        expected: Dict[str, Any] = {
            'timestamp:UNQUOTED': 123456789,
            'name': 'last_updated_timestamp',
            'KEY': 'product_id_dashboard://cluster_id.dashboard_group_id/dashboard_id/_last_modified_timestamp',
            'LABEL': 'Timestamp'
        }

        assert actual is not None
        self.assertDictEqual(actual_serialized, expected)
        self.assertIsNone(dashboard_last_modified.create_next_node())

    def test_dashboard_owner_relations(self) -> None:
        dashboard_last_modified = DashboardLastModifiedTimestamp(last_modified_timestamp=123456789,
                                                                 cluster='cluster_id',
                                                                 product='product_id',
                                                                 dashboard_id='dashboard_id',
                                                                 dashboard_group_id='dashboard_group_id')

        actual = dashboard_last_modified.create_next_relation()
        actual_serialized = neo4_serializer.serialize_relationship(actual)
        expected: Dict[str, Any] = {
            RELATION_END_KEY: 'product_id_dashboard://cluster_id.dashboard_group_id/dashboard_id'
                              '/_last_modified_timestamp',
            RELATION_START_LABEL: 'Dashboard',
            RELATION_END_LABEL: 'Timestamp',
            RELATION_START_KEY: 'product_id_dashboard://cluster_id.dashboard_group_id/dashboard_id',
            RELATION_TYPE: 'LAST_UPDATED_AT',
            RELATION_REVERSE_TYPE: 'LAST_UPDATED_TIME_OF'
        }

        assert actual is not None
        self.assertDictEqual(actual_serialized, expected)
        self.assertIsNone(dashboard_last_modified.create_next_relation())
