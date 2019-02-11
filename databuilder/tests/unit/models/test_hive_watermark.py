import unittest
from databuilder.models.hive_watermark import HiveWatermark

from databuilder.models.neo4j_csv_serde import NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


CREATE_TIME = '2017-09-18T00:00:00'
SCHEMA = 'BASE'
TABLE = 'TEST'
NESTED_PART = 'ds=2017-09-18/feature_id=9'
CLUSTER = 'DEFAULT'
PART_TYPE = 'LOW_WATERMARK'


class TestHiveWatermark(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        super(TestHiveWatermark, self).setUp()
        self.hive_watermark = HiveWatermark(create_time='2017-09-18T00:00:00',
                                            schema_name=SCHEMA,
                                            table_name=TABLE,
                                            cluster=CLUSTER,
                                            part_type=PART_TYPE,
                                            part_name=NESTED_PART)

        self.expected_node_result = {
            NODE_KEY: 'hive://default.base/test/low_watermark/',
            NODE_LABEL: 'Watermark',
            'partition_key': 'ds',
            'partition_value': '2017-09-18/feature_id=9',
            'create_time': '2017-09-18T00:00:00'
        }

        self.expected_relation_result = {
            RELATION_START_KEY: 'hive://default.base/test/low_watermark/',
            RELATION_START_LABEL: 'Watermark',
            RELATION_END_KEY: 'hive://default.base/test',
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: 'BELONG_TO_TABLE',
            RELATION_REVERSE_TYPE: 'WATERMARK'
        }

    def test_get_watermark_model_key(self):
        # type: () -> None
        watermark = self.hive_watermark.get_watermark_model_key()
        self.assertEquals(watermark, 'hive://default.base/test/low_watermark/')

    def test_get_metadata_model_key(self):
        # type: () -> None
        metadata = self.hive_watermark.get_metadata_model_key()
        self.assertEquals(metadata, 'hive://default.base/test')

    def test_create_nodes(self):
        # type: () -> None
        nodes = self.hive_watermark.create_nodes()
        self.assertEquals(len(nodes), 1)
        self.assertEquals(nodes[0], self.expected_node_result)

    def test_create_relation(self):
        # type: () -> None
        relation = self.hive_watermark.create_relation()
        self.assertEquals(len(relation), 1)
        self.assertEquals(relation[0], self.expected_relation_result)

    def test_create_next_node(self):
        # type: () -> None
        next_node = self.hive_watermark.create_next_node()
        self.assertEquals(next_node, self.expected_node_result)

    def test_create_next_relation(self):
        # type: () -> None
        next_relation = self.hive_watermark.create_next_relation()
        self.assertEquals(next_relation, self.expected_relation_result)
