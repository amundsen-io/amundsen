# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import (
    Any, Dict, Iterator, List, Optional, Union,
)

import boto3
import jsonref
from pyhocon import ConfigFactory, ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata

LOGGER = logging.getLogger(__name__)


class EventBridgeExtractor(Extractor):
    """
    Extracts the latest version of all schemas from a given AWS EventBridge schema registry
    """

    REGION_NAME_KEY = "region_name"
    REGISTRY_NAME_KEY = "registry_name"
    DEFAULT_CONFIG = ConfigFactory.from_dict(
        {REGION_NAME_KEY: "us-east-1", REGISTRY_NAME_KEY: "aws.events"}
    )

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(EventBridgeExtractor.DEFAULT_CONFIG)

        boto3.setup_default_session(
            region_name=conf.get(EventBridgeExtractor.REGION_NAME_KEY)
        )
        self._schemas = boto3.client("schemas")

        self._registry_name = conf.get(EventBridgeExtractor.REGISTRY_NAME_KEY)

        self._extract_iter: Union[None, Iterator] = None

    def extract(self) -> Union[TableMetadata, None]:
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter(self._registry_name)
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def get_scope(self) -> str:
        return "extractor.eventbridge"

    def _get_extract_iter(self, registry_name: str) -> Iterator[TableMetadata]:
        """
        It gets all the schemas and yields TableMetadata
        :return:
        """
        for schema_desc in self._get_raw_extract_iter(registry_name):
            if "Content" not in schema_desc:
                LOGGER.warning(
                    f"skipped malformatted schema: {jsonref.dumps(schema_desc)}"
                )
                continue

            content = jsonref.loads(schema_desc["Content"])

            if content.get("openapi", "") == "3.0.0":  # NOTE: OpenAPI 3.0
                title = content.get("info", {}).get("title", "")
                for schema_name, schema in (
                    content.get("components", {}).get("schemas", {}).items()
                ):
                    table = EventBridgeExtractor._build_table(
                        schema,
                        schema_name,
                        registry_name,
                        title,
                        content.get("description", None),
                    )

                    if table is None:
                        continue

                    yield table
            elif (
                content.get("$schema", "") == "http://json-schema.org/draft-04/schema#"
            ):  # NOTE: JSON Schema Draft 4
                title = content.get("title", "")

                for schema_name, schema in content.get("definitions", {}).items():
                    table = EventBridgeExtractor._build_table(
                        schema,
                        schema_name,
                        registry_name,
                        title,
                        schema.get("description", None),
                    )

                    if table is None:
                        continue

                    yield table

                table = EventBridgeExtractor._build_table(
                    content,
                    "Root",
                    registry_name,
                    title,
                    content.get("description", None),
                )

                if table is None:
                    continue

                yield table

            else:
                LOGGER.warning(
                    f"skipped unsupported schema format: {jsonref.dumps(schema_desc)}"
                )
                continue

    def _get_raw_extract_iter(self, registry_name: str) -> Iterator[Dict[str, Any]]:
        """
        Provides iterator of results row from schemas client
        :return:
        """
        schemas_descs = self._search_schemas(registry_name)
        return iter(schemas_descs)

    def _search_schemas(self, registry_name: str) -> List[Dict[str, Any]]:
        """
        Get all schemas descriptions.
        """
        schemas_names = []
        paginator = self._schemas.get_paginator("list_schemas")
        for result in paginator.paginate(RegistryName=registry_name):
            for schema in result["Schemas"]:
                schemas_names.append(schema["SchemaName"])

        schemas_descs = []
        for schema_name in schemas_names:
            schema_versions = []
            paginator = self._schemas.get_paginator("list_schema_versions")
            for result in paginator.paginate(
                RegistryName=registry_name, SchemaName=schema_name
            ):
                schema_versions += result["SchemaVersions"]
            latest_schema_version = EventBridgeExtractor._get_latest_schema_version(
                schema_versions
            )

            schema_desc = self._schemas.describe_schema(
                RegistryName=registry_name,
                SchemaName=schema_name,
                SchemaVersion=latest_schema_version,
            )

            schemas_descs.append(schema_desc)

        return schemas_descs

    @staticmethod
    def _build_table(
        schema: Dict[str, Any],
        schema_name: str,
        registry_name: str,
        title: str,
        description: str,
    ) -> Optional[TableMetadata]:
        columns = []
        for i, (column_name, properties) in enumerate(
            schema.get("properties", {}).items()
        ):
            columns.append(
                ColumnMetadata(
                    column_name,
                    properties.get("description", None),
                    EventBridgeExtractor._get_property_type(properties),
                    i,
                )
            )

        if len(columns) == 0:
            LOGGER.warning(
                f"skipped schema with primitive type: "
                f"{schema_name}: {jsonref.dumps(schema)}"
            )
            return None

        return TableMetadata(
            "eventbridge", registry_name, title, schema_name, description, columns,
        )

    @staticmethod
    def _get_latest_schema_version(schema_versions: List[Dict[str, Any]]) -> str:
        versions = []
        for info in schema_versions:
            version = int(info["SchemaVersion"])
            versions.append(version)
        return str(max(versions))

    @staticmethod
    def _get_property_type(schema: Dict) -> str:
        if "type" not in schema:
            return "object"

        if schema["type"] == "object":
            properties = [
                f"{name}:{EventBridgeExtractor._get_property_type(_schema)}"
                for name, _schema in schema.get("properties", {}).items()
            ]
            if len(properties) > 0:
                return "struct<" + ",".join(properties) + ">"
            return "struct<object>"
        elif schema["type"] == "array":
            items = EventBridgeExtractor._get_property_type(schema.get("items", {}))
            return "array<" + items + ">"
        else:
            if "format" in schema:
                return f"{schema['type']}[{schema['format']}]"
            return schema["type"]
