# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import copy
import unittest

from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata


class TestDashboardMetadata(unittest.TestCase):
    def setUp(self) -> None:
        # Full exammple
        self.dashboard_metadata = DashboardMetadata('Product - Jobs.cz',
                                                    'Agent',
                                                    'Agent dashboard description',
                                                    ['test_tag', 'tag2'],
                                                    dashboard_group_description='foo dashboard group description',
                                                    created_timestamp=123456789,
                                                    dashboard_group_url='https://foo.bar/dashboard_group/foo',
                                                    dashboard_url='https://foo.bar/dashboard_group/foo/dashboard/bar',
                                                    )
        # Without tags
        self.dashboard_metadata2 = DashboardMetadata('Product - Atmoskop',
                                                     'Atmoskop',
                                                     'Atmoskop dashboard description',
                                                     [],
                                                     )

        # One common tag with dashboard_metadata, no description
        self.dashboard_metadata3 = DashboardMetadata('Product - Jobs.cz',
                                                     'Dohazovac',
                                                     '',
                                                     ['test_tag', 'tag3']
                                                     )

        # Necessary minimum -- NOT USED
        self.dashboard_metadata4 = DashboardMetadata('',
                                                     'PzR',
                                                     '',
                                                     []
                                                     )

        self.expected_nodes_deduped = [
            {'KEY': '_dashboard://gold', 'LABEL': 'Cluster', 'name': 'gold'},
            {'created_timestamp': 123456789, 'name': 'Agent', 'KEY': '_dashboard://gold.Product - Jobs.cz/Agent',
             'LABEL': 'Dashboard',
             'dashboard_url': 'https://foo.bar/dashboard_group/foo/dashboard/bar'},
            {'name': 'Product - Jobs.cz', 'KEY': '_dashboard://gold.Product - Jobs.cz', 'LABEL': 'Dashboardgroup',
             'dashboard_group_url': 'https://foo.bar/dashboard_group/foo'},
            {'KEY': '_dashboard://gold.Product - Jobs.cz/_description', 'LABEL': 'Description',
             'description': 'foo dashboard group description'},
            {'description': 'Agent dashboard description',
             'KEY': '_dashboard://gold.Product - Jobs.cz/Agent/_description', 'LABEL': 'Description'},
            {'tag_type': 'dashboard', 'KEY': 'test_tag', 'LABEL': 'Tag'},
            {'tag_type': 'dashboard', 'KEY': 'tag2', 'LABEL': 'Tag'}
        ]

        self.expected_nodes = copy.deepcopy(self.expected_nodes_deduped)

        self.expected_rels_deduped = [
            {'END_KEY': '_dashboard://gold.Product - Jobs.cz', 'END_LABEL': 'Dashboardgroup',
             'REVERSE_TYPE': 'DASHBOARD_GROUP_OF', 'START_KEY': '_dashboard://gold',
             'START_LABEL': 'Cluster', 'TYPE': 'DASHBOARD_GROUP'},
            {'END_KEY': '_dashboard://gold.Product - Jobs.cz/_description', 'END_LABEL': 'Description',
             'REVERSE_TYPE': 'DESCRIPTION_OF', 'START_KEY': '_dashboard://gold.Product - Jobs.cz',
             'START_LABEL': 'Dashboardgroup', 'TYPE': 'DESCRIPTION'},
            {'END_KEY': '_dashboard://gold.Product - Jobs.cz', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Dashboardgroup',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Agent', 'TYPE': 'DASHBOARD_OF',
             'REVERSE_TYPE': 'DASHBOARD'},
            {'END_KEY': '_dashboard://gold.Product - Jobs.cz/Agent/_description', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Description',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Agent', 'TYPE': 'DESCRIPTION',
             'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'test_tag', 'START_LABEL': 'Dashboard', 'END_LABEL': 'Tag',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Agent', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
            {'END_KEY': 'tag2', 'START_LABEL': 'Dashboard', 'END_LABEL': 'Tag',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Agent', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'}
        ]

        self.expected_rels = copy.deepcopy(self.expected_rels_deduped)

        self.expected_nodes_deduped2 = [
            {'KEY': '_dashboard://gold', 'LABEL': 'Cluster', 'name': 'gold'},
            {'name': 'Atmoskop', 'KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop', 'LABEL': 'Dashboard'},
            {'name': 'Product - Atmoskop', 'KEY': '_dashboard://gold.Product - Atmoskop', 'LABEL': 'Dashboardgroup'},
            {'description': 'Atmoskop dashboard description',
             'KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop/_description',
             'LABEL': 'Description'},
        ]

        self.expected_nodes2 = copy.deepcopy(self.expected_nodes_deduped2)

        self.expected_rels_deduped2 = [
            {'END_KEY': '_dashboard://gold.Product - Atmoskop', 'END_LABEL': 'Dashboardgroup',
             'REVERSE_TYPE': 'DASHBOARD_GROUP_OF', 'START_KEY': '_dashboard://gold',
             'START_LABEL': 'Cluster', 'TYPE': 'DASHBOARD_GROUP'},
            {'END_KEY': '_dashboard://gold.Product - Atmoskop', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Dashboardgroup',
             'START_KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop', 'TYPE': 'DASHBOARD_OF',
             'REVERSE_TYPE': 'DASHBOARD'},
            {'END_KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop/_description', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Description',
             'START_KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop', 'TYPE': 'DESCRIPTION',
             'REVERSE_TYPE': 'DESCRIPTION_OF'},
        ]

        self.expected_rels2 = copy.deepcopy(self.expected_rels_deduped2)

        self.expected_nodes_deduped3 = [
            {'KEY': '_dashboard://gold', 'LABEL': 'Cluster', 'name': 'gold'},
            {'name': 'Dohazovac', 'KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac', 'LABEL': 'Dashboard'},
            {'name': 'Product - Jobs.cz', 'KEY': '_dashboard://gold.Product - Jobs.cz', 'LABEL': 'Dashboardgroup'},
            {'tag_type': 'dashboard', 'KEY': 'test_tag', 'LABEL': 'Tag'},
            {'tag_type': 'dashboard', 'KEY': 'tag3', 'LABEL': 'Tag'}
        ]

        self.expected_nodes3 = copy.deepcopy(self.expected_nodes_deduped3)

        self.expected_rels_deduped3 = [
            {'END_KEY': '_dashboard://gold.Product - Jobs.cz', 'END_LABEL': 'Dashboardgroup',
             'REVERSE_TYPE': 'DASHBOARD_GROUP_OF', 'START_KEY': '_dashboard://gold',
             'START_LABEL': 'Cluster', 'TYPE': 'DASHBOARD_GROUP'},
            {'END_KEY': '_dashboard://gold.Product - Jobs.cz', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Dashboardgroup',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac', 'TYPE': 'DASHBOARD_OF',
             'REVERSE_TYPE': 'DASHBOARD'},
            {'END_KEY': 'test_tag', 'START_LABEL': 'Dashboard', 'END_LABEL': 'Tag',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
            {'END_KEY': 'tag3', 'START_LABEL': 'Dashboard', 'END_LABEL': 'Tag',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
        ]

        self.expected_rels3 = copy.deepcopy(self.expected_rels_deduped3)

    def test_serialize(self) -> None:
        # First test
        node_row = self.dashboard_metadata.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.dashboard_metadata.next_node()

        self.assertEqual(self.expected_nodes, actual)

        relation_row = self.dashboard_metadata.next_relation()
        actual = []
        while relation_row:
            actual.append(relation_row)
            relation_row = self.dashboard_metadata.next_relation()

        self.assertEqual(self.expected_rels, actual)

        # Second test
        node_row = self.dashboard_metadata2.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.dashboard_metadata2.next_node()

        self.assertEqual(self.expected_nodes_deduped2, actual)

        relation_row = self.dashboard_metadata2.next_relation()
        actual = []
        while relation_row:
            actual.append(relation_row)
            relation_row = self.dashboard_metadata2.next_relation()

        self.assertEqual(self.expected_rels_deduped2, actual)

        # Third test
        node_row = self.dashboard_metadata3.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.dashboard_metadata3.next_node()

        self.assertEqual(self.expected_nodes_deduped3, actual)

        relation_row = self.dashboard_metadata3.next_relation()
        actual = []
        while relation_row:
            actual.append(relation_row)
            relation_row = self.dashboard_metadata3.next_relation()

        self.assertEqual(self.expected_rels_deduped3, actual)


if __name__ == '__main__':
    unittest.main()
