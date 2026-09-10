# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import unittest
from typing import (
    Any, Dict, List,
)

from mock import patch
from pyhocon import ConfigFactory

from databuilder.extractor.eventbridge_extractor import EventBridgeExtractor
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata

registry_name = "TestAmundsen"

test_schema_openapi_3 = {
    "openapi": "3.0.0",
    "info": {"version": "1.0.0", "title": "OrderConfirmed"},
    "paths": {},
    "components": {
        "schemas": {
            "AWSEvent": {
                "type": "object",
                "required": [
                    "detail-type",
                    "resources",
                    "detail",
                    "id",
                    "source",
                    "time",
                    "region",
                    "account",
                ],
                "properties": {
                    "detail": {"$ref": "#/components/schemas/OrderConfirmed"},
                    "account": {"type": "string"},
                    "detail-type": {"type": "string"},
                    "id": {"type": "string"},
                    "region": {"type": "string"},
                    "resources": {"type": "array", "items": {"type": "string"}},
                    "source": {"type": "string"},
                    "time": {"type": "string", "format": "date-time"},
                },
            },
            "OrderConfirmed": {
                "type": "object",
                "properties": {
                    "id": {"type": "number", "format": "int64"},
                    "status": {"type": "string"},
                    "currency": {"type": "string"},
                    "customer": {"$ref": "#/components/schemas/Customer"},
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Item"},
                    },
                },
            },
            "Customer": {
                "type": "object",
                "properties": {
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {},
                },
                "description": "customer description",
            },
            "Item": {
                "type": "object",
                "properties": {
                    "sku": {"type": "number", "format": "int64"},
                    "name": {"type": "string"},
                    "price": {"type": "number", "format": "double"},
                    "quantity": {"type": "number", "format": "int32"},
                },
            },
            "PrimitiveSchema": {"type": "bool"},
        }
    },
}

openapi_3_item_type = (
    "struct<sku:number[int64],name:string,price:number[double],quantity:number[int32]>"
)
openapi_3_customer_type = (
    "struct<firstName:string,lastName:string,email:string,phone:object>"
)
openapi_3_order_confirmed_type = (
    f"struct<id:number[int64],status:string,currency:string,"
    f"customer:{openapi_3_customer_type},items:array<{openapi_3_item_type}>>"
)

expected_openapi_3_tables = [
    TableMetadata(
        "eventbridge",
        registry_name,
        "OrderConfirmed",
        "AWSEvent",
        None,
        [
            ColumnMetadata("detail", None, openapi_3_order_confirmed_type, 0),
            ColumnMetadata("account", None, "string", 1),
            ColumnMetadata("detail-type", None, "string", 2),
            ColumnMetadata("id", None, "string", 3),
            ColumnMetadata("region", None, "string", 4),
            ColumnMetadata("resources", None, "array<string>", 5),
            ColumnMetadata("source", None, "string", 6),
            ColumnMetadata("time", None, "string[date-time]", 7),
        ],
        False,
    ),
    TableMetadata(
        "eventbridge",
        registry_name,
        "OrderConfirmed",
        "OrderConfirmed",
        None,
        [
            ColumnMetadata("id", None, "number[int64]", 0),
            ColumnMetadata("status", None, "string", 1),
            ColumnMetadata("currency", None, "string", 2),
            ColumnMetadata(
                "customer", "customer description", openapi_3_customer_type, 3,
            ),
            ColumnMetadata("items", None, f"array<{openapi_3_item_type}>", 4),
        ],
        False,
    ),
    TableMetadata(
        "eventbridge",
        registry_name,
        "OrderConfirmed",
        "Customer",
        None,
        [
            ColumnMetadata("firstName", None, "string", 0),
            ColumnMetadata("lastName", None, "string", 1),
            ColumnMetadata("email", None, "string", 2),
            ColumnMetadata("phone", None, "object", 3),
        ],
        False,
    ),
    TableMetadata(
        "eventbridge",
        registry_name,
        "OrderConfirmed",
        "Item",
        None,
        [
            ColumnMetadata("sku", None, "number[int64]", 0),
            ColumnMetadata("name", None, "string", 1),
            ColumnMetadata("price", None, "number[double]", 2),
            ColumnMetadata("quantity", None, "number[int32]", 3),
        ],
        False,
    ),
]

test_schema_json_draft_4 = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "The root schema",
    "description": "The root schema comprises the entire JSON document.",
    "required": [
        "version",
        "id",
        "detail-type",
        "source",
        "account",
        "time",
        "region",
        "resources",
        "detail",
    ],
    "definitions": {
        "BookingDone": {
            "type": "object",
            "properties": {"booking": {"$ref": "#/definitions/Booking"}},
        },
        "Booking": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "status": {"type": "string"},
                "customer": {"$ref": "#/definitions/Customer"},
            },
            "required": ["id", "status", "customer"],
        },
        "Customer": {
            "type": "object",
            "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
            "required": ["id", "name"],
        },
    },
    "properties": {
        "version": {
            "$id": "#/properties/version",
            "type": "string",
            "description": "version description",
        },
        "id": {"$id": "#/properties/id", "type": "string"},
        "detail-type": {"$id": "#/properties/detail-type", "type": "string"},
        "source": {"$id": "#/properties/source", "type": "string"},
        "account": {"$id": "#/properties/account", "type": "string"},
        "time": {"$id": "#/properties/time", "type": "string"},
        "region": {"$id": "#/properties/region", "type": "string"},
        "resources": {
            "$id": "#/properties/resources",
            "type": "array",
            "additionalItems": True,
            "items": {"$id": "#/properties/resources/items", "type": "string"},
        },
        "detail": {"$ref": "#/definitions/BookingDone"},
    },
}

json_draft_4_customer_type = "struct<id:string,name:string>"
json_draft_4_booking_type = (
    f"struct<id:string,status:string,customer:{json_draft_4_customer_type}>"
)
json_draft_4_booking_done_type = f"struct<booking:{json_draft_4_booking_type}>"

expected_json_draft_4_tables = [
    TableMetadata(
        "eventbridge",
        registry_name,
        "The root schema",
        "BookingDone",
        None,
        [ColumnMetadata("booking", None, json_draft_4_booking_type, 0)],
        False,
    ),
    TableMetadata(
        "eventbridge",
        registry_name,
        "The root schema",
        "Booking",
        None,
        [
            ColumnMetadata("id", None, "string", 0),
            ColumnMetadata("status", None, "string", 1),
            ColumnMetadata("customer", None, json_draft_4_customer_type, 2),
        ],
        False,
    ),
    TableMetadata(
        "eventbridge",
        registry_name,
        "The root schema",
        "Customer",
        None,
        [
            ColumnMetadata("id", None, "string", 0),
            ColumnMetadata("name", None, "string", 1),
        ],
        False,
    ),
    TableMetadata(
        "eventbridge",
        registry_name,
        "The root schema",
        "Root",
        "The root schema comprises the entire JSON document.",
        [
            ColumnMetadata("version", "version description", "string", 0),
            ColumnMetadata("id", None, "string", 1),
            ColumnMetadata("detail-type", None, "string", 2),
            ColumnMetadata("source", None, "string", 3),
            ColumnMetadata("account", None, "string", 4),
            ColumnMetadata("time", None, "string", 5),
            ColumnMetadata("region", None, "string", 6),
            ColumnMetadata("resources", None, "array<string>", 7),
            ColumnMetadata("detail", None, json_draft_4_booking_done_type, 8),
        ],
        False,
    ),
]

schema_versions = [
    {"SchemaVersion": "1"},
    {"SchemaVersion": "2"},
    {"SchemaVersion": "3"},
]

expected_schema_version = "3"

property_types: List[Dict[Any, Any]] = [
    {"NoType": ""},
    {"type": "object", "NoProperties": {}},
    {
        "type": "object",
        "properties": {
            "property_1": {"type": "string"},
            "property_2": {"type": "number"},
        },
    },
    {
        "type": "object",
        "properties": {
            "property_1": {
                "type": "object",
                "properties": {
                    "property_1_1": {"type": "string"},
                    "property_1_2": {"type": "number", "format": "int64"},
                },
            },
            "property_2": {"type": "number"},
        },
    },
    {"type": "array", "NoItems": {}},
    {"type": "array", "items": {"type": "string"}},
    {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "property_1": {"type": "string"},
                "property_2": {"type": "number"},
            },
        },
    },
    {"type": "string"},
    {"type": "string", "format": "date-time"},
]

expected_property_types = [
    "object",
    "struct<object>",
    "struct<property_1:string,property_2:number>",
    "struct<property_1:struct<property_1_1:string,property_1_2:number[int64]>,property_2:number>",
    "array<object>",
    "array<string>",
    "array<struct<property_1:string,property_2:number>>",
    "string",
    "string[date-time]",
]


# patch whole class to avoid actually calling for boto3.client during tests
@patch("databuilder.extractor.eventbridge_extractor.boto3.client", lambda x: None)
class TestEventBridgeExtractor(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)

        self.conf = ConfigFactory.from_dict(
            {EventBridgeExtractor.REGISTRY_NAME_KEY: registry_name}
        )
        self.maxDiff = None

    def test_extraction_with_empty_query_result(self) -> None:
        """
        Test Extraction with empty result from query
        """
        with patch.object(EventBridgeExtractor, "_search_schemas") as mock_search:
            mock_search.return_value = []

            extractor = EventBridgeExtractor()
            extractor.init(self.conf)

            results = extractor.extract()
            self.assertEqual(results, None)

    def test_extraction_no_content(self) -> None:
        with patch.object(EventBridgeExtractor, "_search_schemas") as mock_search:
            mock_search.return_value = [{"NoContent": {}}]

            extractor = EventBridgeExtractor()
            extractor.init(self.conf)

            results = extractor.extract()
            self.assertEqual(results, None)

    def test_extraction_unsupported_format(self) -> None:
        with patch.object(EventBridgeExtractor, "_search_schemas") as mock_search:
            mock_search.return_value = [{"Content": json.dumps({})}]

            extractor = EventBridgeExtractor()
            extractor.init(self.conf)

            results = extractor.extract()
            self.assertEqual(results, None)

    def test_extraction_with_single_result_openapi_3(self) -> None:
        with patch.object(EventBridgeExtractor, "_search_schemas") as mock_search:
            mock_search.return_value = [{"Content": json.dumps(test_schema_openapi_3)}]

            extractor = EventBridgeExtractor()
            extractor.init(self.conf)

            for expected_table in expected_openapi_3_tables:
                self.assertEqual(
                    expected_table.__repr__(), extractor.extract().__repr__()
                )
            self.assertIsNone(extractor.extract())

    def test_extraction_with_single_result_json_draft_4(self) -> None:
        with patch.object(EventBridgeExtractor, "_search_schemas") as mock_search:
            mock_search.return_value = [
                {"Content": json.dumps(test_schema_json_draft_4)}
            ]

            extractor = EventBridgeExtractor()
            extractor.init(self.conf)

            for expected_table in expected_json_draft_4_tables:
                self.assertEqual(
                    expected_table.__repr__(), extractor.extract().__repr__()
                )
            self.assertIsNone(extractor.extract())

    def test_extraction_with_multiple_result(self) -> None:
        with patch.object(EventBridgeExtractor, "_search_schemas") as mock_search:
            mock_search.return_value = [
                {"Content": json.dumps(test_schema_openapi_3)},
                {"Content": json.dumps(test_schema_json_draft_4)},
            ]

            extractor = EventBridgeExtractor()
            extractor.init(self.conf)

            for expected_schema in expected_openapi_3_tables:
                self.assertEqual(
                    expected_schema.__repr__(), extractor.extract().__repr__()
                )

            for expected_table in expected_json_draft_4_tables:
                self.assertEqual(
                    expected_table.__repr__(), extractor.extract().__repr__()
                )

            self.assertIsNone(extractor.extract())

    def test_get_latest_schema_version(self) -> None:
        self.assertEqual(
            EventBridgeExtractor._get_latest_schema_version(schema_versions),
            expected_schema_version,
        )

    def test_get_property_type(self) -> None:
        for property_type, expected_property_type in zip(
            property_types, expected_property_types
        ):
            self.assertEqual(
                EventBridgeExtractor._get_property_type(property_type),
                expected_property_type,
            )


if __name__ == "__main__":
    unittest.main()
