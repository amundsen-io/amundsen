# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from databuilder.models.watermark import Watermark

from databuilder.models.neo4j_csv_serde import NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


CREATE_TIME = '2017-09-18T00:00:00'
DATABASE = 'DYNAMO'
SCHEMA = 'BASE'
TABLE = 'TEST'
NESTED_PART = 'ds=2017-09-18/feature_id=9'
CLUSTER = 'DEFAULT'
PART_TYPE = 'LOW_WATERMARK'


class TestWatermark(unittest.TestCase):

    def setUp(self) -> None:
        super(TestWatermark, self).setUp()
        self.watermark = Watermark(create_time='2017-09-18T00:00:00',
                                   database=DATABASE,
                                   schema=SCHEMA,
                                   table_name=TABLE,
                                   cluster=CLUSTER,
                                   part_type=PART_TYPE,
                                   part_name=NESTED_PART)

        self.expected_node_result = {
            NODE_KEY: '{database}://{cluster}.{schema}/{table}/{part_type}/'
            .format(
                database=DATABASE.lower(),
                cluster=CLUSTER.lower(),
                schema=SCHEMA.lower(),
                table=TABLE.lower(),
                part_type=PART_TYPE.lower()),
            NODE_LABEL: 'Watermark',
            'partition_key': 'ds',
            'partition_value': '2017-09-18/feature_id=9',
            'create_time': '2017-09-18T00:00:00'
        }

        self.expected_relation_result = {
            RELATION_START_KEY: '{database}://{cluster}.{schema}/{table}/{part_type}/'
            .format(
                database=DATABASE.lower(),
                cluster=CLUSTER.lower(),
                schema=SCHEMA.lower(),
                table=TABLE.lower(),
                part_type=PART_TYPE.lower()),
            RELATION_START_LABEL: 'Watermark',
            RELATION_END_KEY: '{database}://{cluster}.{schema}/{table}'
            .format(
                database=DATABASE.lower(),
                cluster=CLUSTER.lower(),
                schema=SCHEMA.lower(),
                table=TABLE.lower()),
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: 'BELONG_TO_TABLE',
            RELATION_REVERSE_TYPE: 'WATERMARK'
        }

    def test_get_watermark_model_key(self) -> None:
        watermark = self.watermark.get_watermark_model_key()
        self.assertEquals(
            watermark, '{database}://{cluster}.{schema}/{table}/{part_type}/'
            .format(database=DATABASE.lower(),
                    cluster=CLUSTER.lower(),
                    schema=SCHEMA.lower(),
                    table=TABLE.lower(),
                    part_type=PART_TYPE.lower()))

    def test_get_metadata_model_key(self) -> None:
        metadata = self.watermark.get_metadata_model_key()
        self.assertEquals(metadata, '{database}://{cluster}.{schema}/{table}'
                          .format(database=DATABASE.lower(),
                                  cluster=CLUSTER.lower(),
                                  schema=SCHEMA.lower(),
                                  table=TABLE.lower()))

    def test_create_nodes(self) -> None:
        nodes = self.watermark.create_nodes()
        self.assertEquals(len(nodes), 1)
        self.assertEquals(nodes[0], self.expected_node_result)

    def test_create_relation(self) -> None:
        relation = self.watermark.create_relation()
        self.assertEquals(len(relation), 1)
        self.assertEquals(relation[0], self.expected_relation_result)

    def test_create_next_node(self) -> None:
        next_node = self.watermark.create_next_node()
        self.assertEquals(next_node, self.expected_node_result)

    def test_create_next_relation(self) -> None:
        next_relation = self.watermark.create_next_relation()
        self.assertEquals(next_relation, self.expected_relation_result)
