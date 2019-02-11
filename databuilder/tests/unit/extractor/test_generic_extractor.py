import unittest

from pyhocon import ConfigFactory  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.generic_extractor import GenericExtractor


class TestGenericExtractor(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        config_dict = {
            'extractor.generic.extraction_items': [{'timestamp': 10000000}],
            'extractor.generic.model_class':
                'databuilder.models.neo4j_es_last_updated.Neo4jESLastUpdated',
        }
        self.conf = ConfigFactory.from_dict(config_dict)

    def test_extraction_with_model_class(self):
        # type: () -> None
        """
        Test Extraction using model class
        """
        extractor = GenericExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=self.conf,
                                              scope=extractor.get_scope()))

        result = extractor.extract()
        self.assertEquals(result.timestamp, 10000000)
