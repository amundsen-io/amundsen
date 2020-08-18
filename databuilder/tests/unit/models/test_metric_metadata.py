# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import copy
import unittest

from databuilder.models.metric_metadata import MetricMetadata


class TestMetricMetadata(unittest.TestCase):
    def setUp(self) -> None:

        self.metric_metadata = MetricMetadata('Product - Jobs.cz',
                                              'Agent',
                                              'Metric 1',
                                              'a/b*(2*x)',
                                              'This is description of Metric 1',
                                              'MasterMetric',
                                              ['Dummy Metric TAG', 'TAG2'])

        self.metric_metadata2 = MetricMetadata('Product - Jobs.cz',
                                               'Agent',
                                               'Metric 2',
                                               'b/a*(2*x)',
                                               'M2 This is description of Metric 2',
                                               'MasterMetric',
                                               ['Dummy Metric TAG'])

        self.metric_metadata3 = MetricMetadata('Product - Atmoskop',
                                               'Atmoskop',
                                               'Metric 3',
                                               'x*x*x',
                                               '',
                                               '',
                                               [])

        self.expected_nodes_deduped = [
            {'name': 'Metric 1', 'KEY': 'metric://Metric 1', 'LABEL': 'Metric', 'expression': 'a/b*(2*x)'},
            {'description': 'This is description of Metric 1', 'KEY': 'metric://Metric 1/_description',
             'LABEL': 'Description'},
            {'tag_type': 'metric', 'KEY': 'Dummy Metric TAG', 'LABEL': 'Tag'},
            {'tag_type': 'metric', 'KEY': 'TAG2', 'LABEL': 'Tag'},
            {'name': 'MasterMetric', 'KEY': 'type://MasterMetric', 'LABEL': 'Metrictype'}
        ]

        self.expected_nodes = copy.deepcopy(self.expected_nodes_deduped)

        self.expected_rels_deduped = [
            {'END_KEY': 'Product - Jobs.cz://Agent', 'START_LABEL': 'Metric',
             'END_LABEL': 'Dashboard',
             'START_KEY': 'metric://Metric 1', 'TYPE': 'METRIC_OF', 'REVERSE_TYPE': 'METRIC'},
            {'END_KEY': 'metric://Metric 1/_description', 'START_LABEL': 'Metric',
             'END_LABEL': 'Description',
             'START_KEY': 'metric://Metric 1', 'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'Dummy Metric TAG', 'START_LABEL': 'Metric', 'END_LABEL': 'Tag',
             'START_KEY': 'metric://Metric 1', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
            {'END_KEY': 'TAG2', 'START_LABEL': 'Metric', 'END_LABEL': 'Tag',
             'START_KEY': 'metric://Metric 1', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
            {'END_KEY': 'type://MasterMetric', 'START_LABEL': 'Metric',
             'END_LABEL': 'Metrictype', 'START_KEY': 'metric://Metric 1',
             'TYPE': 'METRIC_TYPE', 'REVERSE_TYPE': 'METRIC_TYPE_OF'}
        ]

        self.expected_rels = copy.deepcopy(self.expected_rels_deduped)

        self.expected_nodes_deduped2 = [
            {'name': 'Metric 2', 'KEY': 'metric://Metric 2', 'LABEL': 'Metric', 'expression': 'b/a*(2*x)'},
            {'description': 'M2 This is description of Metric 2', 'KEY': 'metric://Metric 2/_description',
             'LABEL': 'Description'},
            {'tag_type': 'metric', 'KEY': 'Dummy Metric TAG', 'LABEL': 'Tag'},
            {'name': 'MasterMetric', 'KEY': 'type://MasterMetric', 'LABEL': 'Metrictype'}
        ]

        self.expected_nodes2 = copy.deepcopy(self.expected_nodes_deduped2)

        self.expected_rels_deduped2 = [
            {'END_KEY': 'Product - Jobs.cz://Agent', 'START_LABEL': 'Metric',
             'END_LABEL': 'Dashboard',
             'START_KEY': 'metric://Metric 2', 'TYPE': 'METRIC_OF', 'REVERSE_TYPE': 'METRIC'},
            {'END_KEY': 'metric://Metric 2/_description', 'START_LABEL': 'Metric',
             'END_LABEL': 'Description',
             'START_KEY': 'metric://Metric 2', 'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'Dummy Metric TAG', 'START_LABEL': 'Metric', 'END_LABEL': 'Tag',
             'START_KEY': 'metric://Metric 2', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
            {'START_LABEL': 'Metric', 'END_KEY': 'type://MasterMetric',
             'END_LABEL': 'Metrictype', 'START_KEY': 'metric://Metric 2',
             'TYPE': 'METRIC_TYPE', 'REVERSE_TYPE': 'METRIC_TYPE_OF'}
        ]

        self.expected_rels2 = copy.deepcopy(self.expected_rels_deduped2)

        self.expected_nodes_deduped3 = [
            {'name': 'Metric 3', 'KEY': 'metric://Metric 3', 'LABEL': 'Metric', 'expression': 'x*x*x'}
        ]

        self.expected_nodes3 = copy.deepcopy(self.expected_nodes_deduped3)

        self.expected_rels_deduped3 = [
            {'END_KEY': 'Product - Atmoskop://Atmoskop', 'START_LABEL': 'Metric',
             'END_LABEL': 'Dashboard',
             'START_KEY': 'metric://Metric 3', 'TYPE': 'METRIC_OF', 'REVERSE_TYPE': 'METRIC'}
        ]

        self.expected_rels3 = copy.deepcopy(self.expected_rels_deduped3)

    def test_serialize(self) -> None:
        # First test
        node_row = self.metric_metadata.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.metric_metadata.next_node()

        self.assertEqual(self.expected_nodes, actual)

        relation_row = self.metric_metadata.next_relation()
        actual = []
        while relation_row:
            actual.append(relation_row)
            relation_row = self.metric_metadata.next_relation()

        self.assertEqual(self.expected_rels, actual)

        # Second test
        node_row = self.metric_metadata2.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.metric_metadata2.next_node()

        self.assertEqual(self.expected_nodes_deduped2, actual)

        relation_row = self.metric_metadata2.next_relation()
        actual = []
        while relation_row:
            actual.append(relation_row)
            relation_row = self.metric_metadata2.next_relation()

        self.assertEqual(self.expected_rels_deduped2, actual)

        # Third test
        node_row = self.metric_metadata3.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.metric_metadata3.next_node()

        self.assertEqual(self.expected_nodes_deduped3, actual)

        relation_row = self.metric_metadata3.next_relation()
        actual = []
        while relation_row:
            actual.append(relation_row)
            relation_row = self.metric_metadata3.next_relation()

        self.assertEqual(self.expected_rels_deduped3, actual)


if __name__ == '__main__':
    unittest.main()
