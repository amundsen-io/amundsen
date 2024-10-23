# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from pyhocon import ConfigFactory

from databuilder import Scoped
from databuilder.extractor.openlineage_extractor import OpenLineageTableLineageExtractor


class TestOpenlineageExtractor(unittest.TestCase):

    def test_amundsen_dataset_key(self) -> None:
        """
        Test _amundsen_dataset_key method
        """
        config_dict = {
            f'extractor.openlineage_tablelineage.{OpenLineageTableLineageExtractor.TABLE_LINEAGE_FILE_LOCATION}':
                'example/sample_data/openlineage/sample_openlineage_events.ndjson',
            f'extractor.openlineage_tablelineage.{OpenLineageTableLineageExtractor.CLUSTER_NAME}': 'datalab',

        }
        self.conf = ConfigFactory.from_dict(config_dict)
        extractor = OpenLineageTableLineageExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=self.conf,
                                              scope=extractor.get_scope()))

        mock_dataset = {'name': 'mock_table',
                        'namespace': 'postgresql',
                        'database': 'testdb'}

        self.assertEqual('postgresql://datalab.testdb/mock_table', extractor._amundsen_dataset_key(mock_dataset))
        extractor.ol_namespace_override = 'hive'
        self.assertEqual('hive://datalab.testdb/mock_table', extractor._amundsen_dataset_key(mock_dataset))

    def test_extraction_with_model_class(self) -> None:
        """
        Test Extraction
        """
        config_dict = {
            f'extractor.openlineage_tablelineage.{OpenLineageTableLineageExtractor.TABLE_LINEAGE_FILE_LOCATION}':
                'example/sample_data/openlineage/sample_openlineage_events.ndjson',
            f'extractor.openlineage_tablelineage.{OpenLineageTableLineageExtractor.CLUSTER_NAME}': 'datalab',

        }
        self.conf = ConfigFactory.from_dict(config_dict)
        extractor = OpenLineageTableLineageExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=self.conf,
                                              scope=extractor.get_scope()))
        result = extractor.extract()

        self.assertEqual('hive://datalab.test/source_table1', result.table_key)
        self.assertEqual(['hive://datalab.test/destination_table'], result.downstream_deps)

        result2 = extractor.extract()

        self.assertEqual('hive://datalab.test/source_table1', result2.table_key)
        self.assertEqual(['hive://datalab.test/destination_table2'], result2.downstream_deps)

        result3 = extractor.extract()
        self.assertEqual('hive://datalab.test/source_table1', result3.table_key)
        self.assertEqual(['hive://datalab.test/destination_table'], result3.downstream_deps)

        result4 = extractor.extract()
        self.assertEqual('hive://datalab.test/source_table1', result4.table_key)
        self.assertEqual(['hive://datalab.test/destination_table4'], result4.downstream_deps)

        result5 = extractor.extract()
        self.assertEqual('hive://datalab.test/source_table2', result5.table_key)
        self.assertEqual(['hive://datalab.test/destination_table7'], result5.downstream_deps)

        result6 = extractor.extract()
        self.assertEqual('hive://datalab.test/source_table3', result6.table_key)
        self.assertEqual(['hive://datalab.test/destination_table11'], result6.downstream_deps)

        result7 = extractor.extract()
        self.assertEqual('hive://datalab.test/source_table3', result7.table_key)
        self.assertEqual(['hive://datalab.test/destination_table10'], result7.downstream_deps)
