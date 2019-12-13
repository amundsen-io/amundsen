import unittest
from databuilder.extractor.neo4j_metric_search_data_extractor import Neo4jMetricSearchDataExtractor


class TestNeo4jMetricExtractor(unittest.TestCase):

    def test_adding_filter(self):
        # type: (Any) -> None
        extractor = Neo4jMetricSearchDataExtractor()
        actual = extractor._add_publish_tag_filter('foo', 'MATCH (metric:Metric) {publish_tag_filter} RETURN metric')

        self.assertEqual(actual, """MATCH (metric:Metric) WHERE metric.published_tag = 'foo' RETURN metric""")

    def test_not_adding_filter(self):
        # type: (Any) -> None
        extractor = Neo4jMetricSearchDataExtractor()
        actual = extractor._add_publish_tag_filter('', 'MATCH (metric:Metric) {publish_tag_filter} RETURN metric')

        self.assertEqual(actual, """MATCH (metric:Metric)  RETURN metric""")


if __name__ == '__main__':
    unittest.main()
