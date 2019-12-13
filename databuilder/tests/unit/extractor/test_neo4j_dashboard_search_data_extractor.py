import unittest
from databuilder.extractor.neo4j_dashboard_search_data_extractor import Neo4jDashboardSearchDataExtractor


class TestNeo4jDashboardExtractor(unittest.TestCase):

    def test_adding_filter(self):
        # type: (Any) -> None
        extractor = Neo4jDashboardSearchDataExtractor()
        actual = extractor._add_publish_tag_filter(
            'foo', 'MATCH (dashboard:Dashboard) {publish_tag_filter} RETURN dashboard')

        self.assertEqual(
            actual, """MATCH (dashboard:Dashboard) WHERE dashboard.published_tag = 'foo' RETURN dashboard""")

    def test_not_adding_filter(self):
        # type: (Any) -> None
        extractor = Neo4jDashboardSearchDataExtractor()
        actual = extractor._add_publish_tag_filter(
            '', 'MATCH (dashboard:Dashboard) {publish_tag_filter} RETURN dashboard')

        self.assertEqual(actual, """MATCH (dashboard:Dashboard)  RETURN dashboard""")


if __name__ == '__main__':
    unittest.main()
