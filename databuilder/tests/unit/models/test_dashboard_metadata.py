import copy
import unittest

from databuilder.models.dashboard_metadata import DashboardMetadata


class TestDashboardMetadata(unittest.TestCase):
    def setUp(self):
        # type: () -> None
        # Full exammple
        self.dashboard_metadata = DashboardMetadata('Product - Jobs.cz',
                                                    'Agent',
                                                    'Agent dashboard description',
                                                    '2019-05-30T07:03:35.580Z',
                                                    'roald.amundsen@example.org',
                                                    ['test_tag', 'tag2'],
                                                    dashboard_group_description='foo dashboard group description'
                                                    )
        # Without tags
        self.dashboard_metadata2 = DashboardMetadata('Product - Atmoskop',
                                                     'Atmoskop',
                                                     'Atmoskop dashboard description',
                                                     '2019-05-30T07:07:42.326Z',
                                                     'buzz@example.org',
                                                     []
                                                     )

        # One common tag with dashboard_metadata, no description
        self.dashboard_metadata3 = DashboardMetadata('Product - Jobs.cz',
                                                     'Dohazovac',
                                                     '',
                                                     '2019-05-30T07:07:42.326Z',
                                                     'buzz@example.org',
                                                     ['test_tag', 'tag3']
                                                     )

        # Necessary minimum -- NOT USED
        self.dashboard_metadata4 = DashboardMetadata('',
                                                     'PzR',
                                                     '',
                                                     '2019-05-30T07:07:42.326Z',
                                                     '',
                                                     []
                                                     )

        self.expected_nodes_deduped = [
            {'name': 'Agent', 'KEY': '_dashboard://gold.Product - Jobs.cz/Agent', 'LABEL': 'Dashboard'},
            {'name': 'Product - Jobs.cz', 'KEY': '_dashboard://gold.Product - Jobs.cz', 'LABEL': 'Dashboardgroup'},
            {'KEY': '_dashboard://gold.Product - Jobs.cz/_description', 'LABEL': 'Description',
             'description': 'foo dashboard group description'},
            {'description': 'Agent dashboard description',
             'KEY': '_dashboard://gold.Product - Jobs.cz/Agent/_description', 'LABEL': 'Description'},
            {'value': '2019-05-30T07:03:35.580Z',
             'KEY': '_dashboard://gold.Product - Jobs.cz/Agent/_lastreloadtime', 'LABEL': 'Lastreloadtime'},
            {'tag_type': 'dashboard', 'KEY': 'test_tag', 'LABEL': 'Tag'},
            {'tag_type': 'dashboard', 'KEY': 'tag2', 'LABEL': 'Tag'}
        ]

        self.expected_nodes = copy.deepcopy(self.expected_nodes_deduped)

        self.expected_rels_deduped = [
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
            {'END_KEY': '_dashboard://gold.Product - Jobs.cz/Agent/_lastreloadtime', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Lastreloadtime', 'START_KEY': '_dashboard://gold.Product - Jobs.cz/Agent',
             'TYPE': 'LAST_RELOAD_TIME', 'REVERSE_TYPE': 'LAST_RELOAD_TIME_OF'},
            {'END_KEY': 'test_tag', 'START_LABEL': 'Dashboard', 'END_LABEL': 'Tag',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Agent', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
            {'END_KEY': 'tag2', 'START_LABEL': 'Dashboard', 'END_LABEL': 'Tag',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Agent', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
            {'END_KEY': 'roald.amundsen@example.org', 'START_LABEL': 'Dashboard', 'END_LABEL': 'User',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Agent', 'TYPE': 'OWNER', 'REVERSE_TYPE': 'OWNER_OF'}
        ]

        self.expected_rels = copy.deepcopy(self.expected_rels_deduped)

        self.expected_nodes_deduped2 = [
            {'name': 'Atmoskop', 'KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop', 'LABEL': 'Dashboard'},
            {'name': 'Product - Atmoskop', 'KEY': '_dashboard://gold.Product - Atmoskop', 'LABEL': 'Dashboardgroup'},
            {'description': 'Atmoskop dashboard description',
             'KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop/_description',
             'LABEL': 'Description'},
            {'value': '2019-05-30T07:07:42.326Z',
             'KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop/_lastreloadtime',
             'LABEL': 'Lastreloadtime'}
        ]

        self.expected_nodes2 = copy.deepcopy(self.expected_nodes_deduped2)

        self.expected_rels_deduped2 = [
            {'END_KEY': '_dashboard://gold.Product - Atmoskop', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Dashboardgroup',
             'START_KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop', 'TYPE': 'DASHBOARD_OF',
             'REVERSE_TYPE': 'DASHBOARD'},
            {'END_KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop/_description', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Description',
             'START_KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop', 'TYPE': 'DESCRIPTION',
             'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop/_lastreloadtime', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Lastreloadtime', 'START_KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop',
             'TYPE': 'LAST_RELOAD_TIME', 'REVERSE_TYPE': 'LAST_RELOAD_TIME_OF'},
            {'END_KEY': 'buzz@example.org', 'START_LABEL': 'Dashboard', 'END_LABEL': 'User',
             'START_KEY': '_dashboard://gold.Product - Atmoskop/Atmoskop', 'TYPE': 'OWNER', 'REVERSE_TYPE': 'OWNER_OF'}
        ]

        self.expected_rels2 = copy.deepcopy(self.expected_rels_deduped2)

        self.expected_nodes_deduped3 = [
            {'name': 'Dohazovac', 'KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac', 'LABEL': 'Dashboard'},
            {'name': 'Product - Jobs.cz', 'KEY': '_dashboard://gold.Product - Jobs.cz', 'LABEL': 'Dashboardgroup'},
            {'value': '2019-05-30T07:07:42.326Z',
             'KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac/_lastreloadtime', 'LABEL': 'Lastreloadtime'},
            {'tag_type': 'dashboard', 'KEY': 'test_tag', 'LABEL': 'Tag'},
            {'tag_type': 'dashboard', 'KEY': 'tag3', 'LABEL': 'Tag'}
        ]

        self.expected_nodes3 = copy.deepcopy(self.expected_nodes_deduped3)

        self.expected_rels_deduped3 = [
            {'END_KEY': '_dashboard://gold.Product - Jobs.cz', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Dashboardgroup',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac', 'TYPE': 'DASHBOARD_OF',
             'REVERSE_TYPE': 'DASHBOARD'},
            {'END_KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac/_lastreloadtime', 'START_LABEL': 'Dashboard',
             'END_LABEL': 'Lastreloadtime', 'START_KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac',
             'TYPE': 'LAST_RELOAD_TIME', 'REVERSE_TYPE': 'LAST_RELOAD_TIME_OF'},
            {'END_KEY': 'test_tag', 'START_LABEL': 'Dashboard', 'END_LABEL': 'Tag',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
            {'END_KEY': 'tag3', 'START_LABEL': 'Dashboard', 'END_LABEL': 'Tag',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac', 'TYPE': 'TAG', 'REVERSE_TYPE': 'TAG_OF'},
            {'END_KEY': 'buzz@example.org', 'START_LABEL': 'Dashboard', 'END_LABEL': 'User',
             'START_KEY': '_dashboard://gold.Product - Jobs.cz/Dohazovac', 'TYPE': 'OWNER', 'REVERSE_TYPE': 'OWNER_OF'},
        ]

        self.expected_rels3 = copy.deepcopy(self.expected_rels_deduped3)

    def test_serialize(self):
        # type: () -> None
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
