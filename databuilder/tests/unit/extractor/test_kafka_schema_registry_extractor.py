# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import unittest
from typing import List
from unittest.mock import MagicMock

from mock import patch
from pyhocon import ConfigFactory
from schema_registry.client.schema import AvroSchema
from schema_registry.client.utils import SchemaVersion

from databuilder.extractor.kafka_schema_registry_extractor import KafkaSchemaRegistryExtractor
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata

INPUT_SCHEMAS: List[SchemaVersion] = [
    SchemaVersion(
        subject="subject1",
        schema_id=1,
        schema=AvroSchema({
            'type': 'record',
            'namespace': 'com.kubertenes',
            'name': 'AvroDeployment',
            'fields': [
                {'name': 'image', 'type': 'string'},
                {'name': 'replicas', 'type': 'int'},
                {'name': 'port', 'type': 'int'}
            ]
        }),
        version=1
    ),
    SchemaVersion(
        subject="subject2",
        schema_id=2,
        schema=AvroSchema({
                'namespace': 'my.com.ns',
                'name': 'myrecord',
                'type': 'record',
                'fields': [
                    {'name': 'uid', 'type': 'int'},
                    {'name': 'somefield', 'type': 'string'},
                    {'name': 'options',
                        'type':
                        {'type': 'array',
                         'items':
                            {'type': 'record',
                             'name': 'lvl2_record',
                             'fields':
                                [
                                    {'name': 'item1_lvl2', 'type': 'string'},
                                    {'name': 'item2_lvl2',
                                     'type':
                                        {
                                            'type': 'array',
                                            'items':
                                            {
                                                'type': 'record',
                                                'name': 'lvl3_record',
                                                'fields': [
                                                    {'name': 'item1_lvl3',
                                                     'type': 'string'},
                                                    {'name': 'item2_lvl3',
                                                     'type': 'string'}
                                                ]
                                            }
                                        }
                                     }
                                ]
                             }
                         }
                     }
                ]
        }),
        version=1
    ),
    SchemaVersion(
        subject="subject3",
        schema_id=3,
        schema=AvroSchema({
            'type': 'record',
            'name': 'milanoRecord',
            'namespace': 'com.landoop.telecom.telecomitalia.grid',
            'doc': ('Schema for Grid for Telecommunications '
                    'Data from Telecom Italia.'),
            'fields': [
                {'name': 'SquareId',
                 'type': 'int',
                 'doc': (' The id of the square that '
                         'is part of the Milano GRID')},
                {'name': 'Polygon',
                 'type':
                    {'type': 'array',
                     'items': {
                         'type': 'record',
                         'name': 'coordinates',
                         'fields': [
                             {'name': 'longitude', 'type': 'double'},
                             {'name': 'latitude', 'type': 'double'}]}}}]
        }),
        version=5
    )
]
EXPECTED_TABLES: List[TableMetadata] = [
    TableMetadata(
        "kafka_schema_registry",
        "com.kubertenes",
        "subject1",
        "AvroDeployment",
        None,
        [
            ColumnMetadata("image", None, "string", 0),
            ColumnMetadata("replicas", None, "int", 1),
            ColumnMetadata("port", None, "int", 2),
        ],
        False,
    ),
    TableMetadata(
        "kafka_schema_registry",
        "my.com.ns",
        "subject2",
        "myrecord",
        None,
        [
            ColumnMetadata("uid", None, "int", 0),
            ColumnMetadata("somefield", None, "string", 1),
            ColumnMetadata(
                "options",
                None,
                ("array<lvl2_record:struct<"
                 "item1_lvl2:string,item2_lvl2:array<"
                 "lvl3_record:struct<item1_lvl3:string,item2_lvl3:string>>>>"),
                2,
            ),
        ],
        False,
    ),
    TableMetadata(
        "kafka_schema_registry",
        "com.landoop.telecom.telecomitalia.grid",
        "subject3",
        "milanoRecord",
        "Schema for Grid for Telecommunications Data from Telecom Italia.",
        [
            ColumnMetadata(
                "SquareId",
                " The id of the square that is part of the Milano GRID",
                "int",
                0,
            ),
            ColumnMetadata(
                "Polygon",
                None,
                "array<coordinates:struct<longitude:double,latitude:double>>",
                1,
            ),
        ],
        False,
    ),
]


class TestKafkaSchemaRegistryExtractor(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)

        self.conf = ConfigFactory.from_dict(
            {
                KafkaSchemaRegistryExtractor.REGISTRY_URL_KEY: (
                    "http://example.com"
                )
            }
        )
        self.maxDiff = None

    @patch(
        ("databuilder.extractor.kafka_schema_registry_extractor."
         "SchemaRegistryClient.get_subjects")
    )
    def test_extraction_with_empty_query_result(
        self, all_subjects: MagicMock
    ) -> None:
        """
        Test extraction with empty result from query
        """
        all_subjects.return_value = []

        extractor = KafkaSchemaRegistryExtractor()
        extractor.init(self.conf)

        results = extractor.extract()
        self.assertEqual(results, None)

    @patch(
        ("databuilder.extractor.kafka_schema_registry_extractor."
         "SchemaRegistryClient.get_schema")
    )
    @patch(
        ("databuilder.extractor.kafka_schema_registry_extractor."
         "SchemaRegistryClient.get_subjects")
    )
    def test_extraction_successfully(
        self,
        all_subjects: MagicMock,
        schema: MagicMock,
    ) -> None:
        """
        Test extraction with the given schemas finishes successfully
        """
        all_subjects.return_value = [subj.subject for subj in INPUT_SCHEMAS]
        schema.side_effect = INPUT_SCHEMAS

        extractor = KafkaSchemaRegistryExtractor()
        extractor.init(self.conf)

        for expected_table in EXPECTED_TABLES:
            self.assertEqual(
                expected_table.__repr__(), extractor.extract().__repr__()
            )

        self.assertIsNone(extractor.extract())


if __name__ == "__main__":
    unittest.main()
