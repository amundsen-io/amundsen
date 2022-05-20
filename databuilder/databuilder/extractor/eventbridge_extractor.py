# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Union,
)

import boto3
import jsonref
from pyhocon import ConfigFactory, ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata

LOGGER = logging.getLogger(__name__)


class EventBridgeExtractor(Extractor):
    """
    Extracts schemas metadata from AWS EventBridge metastore
    """

    REGISTRY_NAME = "registry_name"
    DEFAULT_CONFIG = ConfigFactory.from_dict({REGISTRY_NAME: "RegistryName"})

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(EventBridgeExtractor.DEFAULT_CONFIG)

        self._schemas = boto3.client("schemas")
        self._registry_name = conf.get(EventBridgeExtractor.REGISTRY_NAME)

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
                continue

            content = jsonref.loads(schema_desc["Content"])

            if "openapi" in content:  # NOTE: OpenAPI 3.0
                title = content["info"]["title"]
                columns = []
                for i, (name, schema) in enumerate(
                    content["components"]["schemas"].items()
                ):
                    columns.append(
                        ColumnMetadata(
                            name,
                            schema.get("description", None),
                            self._get_property_type(schema),
                            i,
                        )
                    )
            else:  # NOTE: JSON Schema Draft 4
                title = content["title"]
                columns = []
                for i, (name, schema) in enumerate(content["properties"].items()):
                    columns.append(
                        ColumnMetadata(
                            name,
                            schema.get("description", None),
                            self._get_property_type(schema),
                            i,
                        )
                    )

            yield TableMetadata(
                "eventbridge",
                "gold",
                title,
                registry_name,
                content.get("description", None),
                columns,
            )

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
        paginator = self._schemas.get_paginator("list_schemas")
        schemas_names = []
        for result in paginator.paginate(RegistryName=registry_name):
            for schema in result["Schemas"]:
                schemas_names.append(schema["SchemaName"])

        schemas_descs = []
        for schema_name in schemas_names:
            schema_versions = []
            data = self._schemas.list_schema_versions(
                RegistryName=registry_name, SchemaName=schema_name
            )
            schema_versions += data["SchemaVersions"]
            while "NextToken" in data:
                token = data["NextToken"]
                data = self._schemas.list_schema_versions(
                    NextToken=token, RegistryName=registry_name, SchemaName=schema_name
                )
                schema_versions += data["SchemaVersions"]
            latest_schema_version = self._get_latest_schema_version(schema_versions)

            schema_desc = self._schemas.describe_schema(
                RegistryName=registry_name,
                SchemaName=schema_name,
                SchemaVersion=latest_schema_version,
            )

            schemas_descs.append(schema_desc)

        return schemas_descs

    def _get_latest_schema_version(self, schema_versions: Dict) -> str:
        versions = []
        for info in schema_versions:
            version = int(info["SchemaVersion"])
            versions.append(version)
        return str(max(versions))

    def _get_property_type(self, schema: dict) -> str:
        if "type" not in schema:
            return ""

        if schema["type"] == "object":
            properties = [
                f"{name}:{self._get_property_type(_schema)}"
                for name, _schema in schema["properties"].items()
            ]
            return "struct<" + ",".join(properties) + ">"
        elif schema["type"] == "array":
            items = self._get_property_type(schema["items"])
            return "array<" + items + ">"
        else:
            return schema["type"]
        # TODO: What to do with format?
