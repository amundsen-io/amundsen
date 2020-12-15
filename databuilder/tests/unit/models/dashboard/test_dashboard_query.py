# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.dashboard.dashboard_query import DashboardQuery
from databuilder.models.graph_serializable import (
    NODE_KEY, NODE_LABEL, RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY,
    RELATION_START_LABEL, RELATION_TYPE,
)
from databuilder.serializers import neo4_serializer


class TestDashboardQuery(unittest.TestCase):

    def test_create_nodes(self) -> None:

        dashboard_query = DashboardQuery(dashboard_group_id='dg_id',
                                         dashboard_id='d_id',
                                         query_id='q_id',
                                         query_name='q_name',
                                         url='http://foo.bar/query/baz',
                                         query_text='SELECT * FROM foo.bar')

        actual = dashboard_query.create_next_node()
        actual_serialized = neo4_serializer.serialize_node(actual)
        expected = {'url': 'http://foo.bar/query/baz', 'name': 'q_name', 'id': 'q_id',
                    'query_text': 'SELECT * FROM foo.bar',
                    NODE_KEY: '_dashboard://gold.dg_id/d_id/query/q_id',
                    NODE_LABEL: DashboardQuery.DASHBOARD_QUERY_LABEL}

        self.assertEqual(expected, actual_serialized)

    def test_create_relation(self) -> None:
        dashboard_query = DashboardQuery(dashboard_group_id='dg_id',
                                         dashboard_id='d_id',
                                         query_id='q_id',
                                         query_name='q_name')

        actual = dashboard_query.create_next_relation()
        actual_serialized = neo4_serializer.serialize_relationship(actual)
        expected = {RELATION_END_KEY: '_dashboard://gold.dg_id/d_id/query/q_id', RELATION_START_LABEL: 'Dashboard',
                    RELATION_END_LABEL: DashboardQuery.DASHBOARD_QUERY_LABEL,
                    RELATION_START_KEY: '_dashboard://gold.dg_id/d_id', RELATION_TYPE: 'HAS_QUERY',
                    RELATION_REVERSE_TYPE: 'QUERY_OF'}

        self.assertEqual(expected, actual_serialized)
