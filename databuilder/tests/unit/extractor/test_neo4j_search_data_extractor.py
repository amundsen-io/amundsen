import unittest
from databuilder.extractor.neo4j_search_data_extractor import Neo4jSearchDataExtractor


class TestNeo4jExtractor(unittest.TestCase):

    def test_adding_filter(self):
        # type: (Any) -> None
        extractor = Neo4jSearchDataExtractor()
        actual = extractor._add_publish_tag_filter('foo', 'MATCH (table:Table) {publish_tag_filter} RETURN table')

        self.assertEqual(actual, """MATCH (table:Table) WHERE table.published_tag = 'foo' RETURN table""")

    def test_not_adding_filter(self):
        # type: (Any) -> None
        extractor = Neo4jSearchDataExtractor()
        actual = extractor._add_publish_tag_filter('', 'MATCH (table:Table) {publish_tag_filter} RETURN table')

        self.assertEqual(actual, """MATCH (table:Table)  RETURN table""")


if __name__ == '__main__':
    unittest.main()
