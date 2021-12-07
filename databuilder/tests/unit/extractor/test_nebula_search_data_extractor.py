# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from typing import Any

from mock import patch
from pyhocon import ConfigFactory

from databuilder import Scoped
from databuilder.extractor.nebula_extractor import NebulaExtractor
from databuilder.extractor.nebula_search_data_extractor import NebulaSearchDataExtractor
from databuilder.publisher.nebula_csv_publisher import JOB_PUBLISH_TAG


class TestNebulaExtractor(unittest.TestCase):

    def test_adding_filter(self: Any) -> None:
        extractor = NebulaSearchDataExtractor()
        actual = extractor._add_publish_tag_filter('foo', 'MATCH (table:Table) {publish_tag_filter} RETURN table')

        self.assertEqual(actual, """MATCH (table:Table) WHERE `table`.`Table`.published_tag == 'foo' RETURN table""")

    def test_not_adding_filter(self: Any) -> None:
        extractor = NebulaSearchDataExtractor()
        actual = extractor._add_publish_tag_filter('', 'MATCH (table:Table) {publish_tag_filter} RETURN table')

        self.assertEqual(actual, """MATCH (table:Table)  RETURN table""")

    def test_default_search_query(self: Any) -> None:
        with patch.object(NebulaExtractor, '_get_connection_pool'):
            extractor = NebulaSearchDataExtractor()
            conf = ConfigFactory.from_dict({
                f'extractor.search_data.extractor.nebula.{NebulaExtractor.NEBULA_ENDPOINTS}': '192.168.11.1:9669',
                f'extractor.search_data.extractor.nebula.{NebulaExtractor.NEBULA_AUTH_USER}': 'test-user',
                f'extractor.search_data.extractor.nebula.{NebulaExtractor.NEBULA_AUTH_PW}': 'test-passwd',
                f'extractor.search_data.{NebulaSearchDataExtractor.ENTITY_TYPE}': 'dashboard',
            })
            extractor.init(Scoped.get_scoped_conf(conf=conf,
                                                  scope=extractor.get_scope()))
            self.assertEqual(extractor.cypher_query, NebulaSearchDataExtractor
                             .DEFAULT_NEBULA_DASHBOARD_CYPHER_QUERY.format(publish_tag_filter=''))

    def test_default_search_query_with_tag(self: Any) -> None:
        with patch.object(NebulaExtractor, '_get_connection_pool'):
            extractor = NebulaSearchDataExtractor()
            conf = ConfigFactory.from_dict({
                f'extractor.search_data.extractor.nebula.{NebulaExtractor.NEBULA_ENDPOINTS}': '192.168.11.1:9669',
                f'extractor.search_data.extractor.nebula.{NebulaExtractor.NEBULA_AUTH_USER}': 'test-user',
                f'extractor.search_data.extractor.nebula.{NebulaExtractor.NEBULA_AUTH_PW}': 'test-passwd',
                f'extractor.search_data.{NebulaSearchDataExtractor.ENTITY_TYPE}': 'dashboard',
                f'extractor.search_data.{JOB_PUBLISH_TAG}': 'test-date',
            })
            extractor.init(Scoped.get_scoped_conf(conf=conf,
                                                  scope=extractor.get_scope()))

            self.assertEqual(extractor.cypher_query,
                             NebulaSearchDataExtractor.DEFAULT_NEBULA_DASHBOARD_CYPHER_QUERY.format
                             (publish_tag_filter="""WHERE `dashboard`.`Dashboard`.published_tag == 'test-date'"""))


if __name__ == '__main__':
    unittest.main()
