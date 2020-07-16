# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.dashboard.dashboard_chart import DashboardChart
from databuilder.models.neo4j_csv_serde import RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


class TestDashboardChart(unittest.TestCase):

    def test_create_nodes(self):
        # type: () -> None

        dashboard_chart = DashboardChart(dashboard_group_id='dg_id',
                                         dashboard_id='d_id',
                                         query_id='q_id',
                                         chart_id='c_id',
                                         chart_name='c_name',
                                         chart_type='bar',
                                         chart_url='http://gold.foo/chart'
                                         )

        actual = dashboard_chart.create_next_node()
        expected = {'name': 'c_name', 'type': 'bar', 'id': 'c_id', 'url': 'http://gold.foo/chart',
                    'KEY': '_dashboard://gold.dg_id/d_id/query/q_id/chart/c_id', 'LABEL': 'Chart'}

        self.assertDictEqual(expected, actual)
        self.assertIsNone(dashboard_chart.create_next_node())

        dashboard_chart = DashboardChart(dashboard_group_id='dg_id',
                                         dashboard_id='d_id',
                                         query_id='q_id',
                                         chart_id='c_id',
                                         chart_url='http://gold.foo.bar/'
                                         )

        actual2 = dashboard_chart.create_next_node()
        expected2 = {'id': 'c_id', 'KEY': '_dashboard://gold.dg_id/d_id/query/q_id/chart/c_id', 'LABEL': 'Chart',
                     'url': 'http://gold.foo.bar/'}
        self.assertDictEqual(expected2, actual2)

    def test_create_relation(self):
        # type: () -> None
        dashboard_chart = DashboardChart(dashboard_group_id='dg_id',
                                         dashboard_id='d_id',
                                         query_id='q_id',
                                         chart_id='c_id',
                                         chart_name='c_name',
                                         chart_type='bar',
                                         )

        actual = dashboard_chart.create_next_relation()
        expected = {RELATION_END_KEY: '_dashboard://gold.dg_id/d_id/query/q_id/chart/c_id',
                    RELATION_START_LABEL: 'Query', RELATION_END_LABEL: 'Chart',
                    RELATION_START_KEY: '_dashboard://gold.dg_id/d_id/query/q_id', RELATION_TYPE: 'HAS_CHART',
                    RELATION_REVERSE_TYPE: 'CHART_OF'}

        self.assertEqual(expected, actual)
        self.assertIsNone(dashboard_chart.create_next_relation())
