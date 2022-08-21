# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
import logging
from asyncio.log import logger
from typing import (
    Any, Dict, Iterator, List, Optional, Union,
)

from pyhocon import ConfigTree
from schema_registry.client import Auth, SchemaRegistryClient
from schema_registry.client.utils import SchemaVersion

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata

LOGGER = logging.getLogger(__name__)


class KafkaSchemaRegistryExtractor(Extractor):
    """
    Extracts the latest version of all schemas from a given
    Kafka Schema Registry URL
    """

    REGISTRY_URL_KEY = "registry_url"
    REGISTRY_USERNAME_KEY = "registry_username"
    REGISTRY_PASSWORD_KEY = "registry_password"

    def init(self, conf: ConfigTree) -> None:
        self._registry_base_url = conf.get(
            KafkaSchemaRegistryExtractor.REGISTRY_URL_KEY
        )

        self._registry_username = conf.get(
            KafkaSchemaRegistryExtractor.REGISTRY_USERNAME_KEY, None
        )

        self._registry_password = conf.get(
            KafkaSchemaRegistryExtractor.REGISTRY_PASSWORD_KEY, None
        )

        # Add authentication if user and password are provided
        if all((self._registry_username, self._registry_password)):
            self._client = SchemaRegistryClient(
                url=self._registry_base_url,
                auth=Auth(
                    username=self._registry_username,
                    password=self._registry_password
                )
            )
        else:
            self._client = SchemaRegistryClient(
                url=self._registry_base_url,
            )

        self._extract_iter: Union[None, Iterator] = None

    def extract(self) -> Union[TableMetadata, None]:
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None
        except Exception as e:
            logger.error(f'Failed to generate next table: {e}')
            return None

    def get_scope(self) -> str:
        return 'extractor.kafka_schema_registry'

    def _get_extract_iter(self) -> Optional[Iterator[TableMetadata]]:
        """
        Return an iterator generating TableMetadata for all of the schemas.
        """
        for schema_version in self._get_raw_extract_iter():
            subject = schema_version.subject
            schema = schema_version.schema.raw_schema
            LOGGER.info((f'Subject: {subject}, '
                         f'Schema: {schema}'))

            try:
                yield KafkaSchemaRegistryExtractor._create_table(
                    schema=schema,
                    subject_name=subject,
                    cluster_name=schema.get(
                        'namespace', 'kafka-schema-registry'
                    ),
                    schema_name=schema.get('name', ''),
                    schema_description=schema.get('doc', None),
                )
            except Exception as e:
                logger.warning(f'Failed to generate table for {subject}: {e}')
                continue

    def _get_raw_extract_iter(self) -> Iterator[SchemaVersion]:
        """
        Return iterator of results row from schema registry
        """
        subjects = self._client.get_subjects()

        LOGGER.info(f'Number of extracted subjects: {len(subjects)}')
        LOGGER.info(f'Extracted subjects: {subjects}')

        for subj in subjects:
            subj_schema = self._client.get_schema(subj)
            LOGGER.info(f'Subject <{subj}> max version: {subj_schema.version}')

            yield subj_schema

    @staticmethod
    def _create_table(
        schema: Dict[str, Any],
        subject_name: str,
        cluster_name: str,
        schema_name: str,
        schema_description: str,
    ) -> Optional[TableMetadata]:
        """
        Create TableMetadata based on given schema and names
        """
        columns: List[ColumnMetadata] = []

        for i, field in enumerate(schema['fields']):
            columns.append(
                ColumnMetadata(
                    name=field['name'],
                    description=field.get('doc', None),
                    col_type=KafkaSchemaRegistryExtractor._get_property_type(
                        field
                    ),
                    sort_order=i,
                )
            )

        return TableMetadata(
            database='kafka_schema_registry',
            cluster=cluster_name,
            schema=subject_name,
            name=schema_name,
            description=schema_description,
            columns=columns,
        )

    @staticmethod
    def _get_property_type(schema: Dict) -> str:
        """
        Return type of the given schema.
        It will also works for nested schema types.
        """
        if 'type' not in schema:
            return 'object'

        if type(schema['type']) is dict:
            return KafkaSchemaRegistryExtractor._get_property_type(
                schema['type']
            )

        # If schema can have multiple types
        if type(schema['type']) is list:
            return '|'.join(schema['type'])

        if schema['type'] == 'record':
            properties = [
                f"{field['name']}:"
                f"{KafkaSchemaRegistryExtractor._get_property_type(field)}"
                for field in schema.get('fields', {})
            ]
            if len(properties) > 0:
                if 'name' in schema:
                    return schema['name'] + \
                        ':struct<' + ','.join(properties) + '>'
                return 'struct<' + ','.join(properties) + '>'
            return 'struct<object>'
        elif schema['type'] == 'array':
            items = KafkaSchemaRegistryExtractor._get_property_type(
                schema.get("items", {})
            )
            return 'array<' + items + '>'
        else:
            return schema['type']
