# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from mock import patch
from typing import Any  # noqa: F401
import unittest

from pyhocon import ConfigFactory  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.neo4j_es_last_updated_extractor import Neo4jEsLastUpdatedExtractor


class TestNeo4jEsLastUpdatedExtractor(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        config_dict = {
            'extractor.neo4j_es_last_updated.model_class':
                'databuilder.models.neo4j_es_last_updated.Neo4jESLastUpdated',
        }
        self.conf = ConfigFactory.from_dict(config_dict)

    @patch('time.time')
    def test_extraction_with_model_class(self, mock_time):
        # type: (Any) -> None
        """
        Test Extraction using model class
        """
        mock_time.return_value = 10000000
        extractor = Neo4jEsLastUpdatedExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=self.conf,
                                              scope=extractor.get_scope()))

        result = extractor.extract()
        self.assertEquals(result.timestamp, 10000000)
