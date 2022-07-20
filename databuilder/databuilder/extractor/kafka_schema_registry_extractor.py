# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
from asyncio.log import logger
import logging
from typing import (
    Any, Dict, Iterator, List, Optional, Union,
)
import json
from pyhocon import ConfigFactory, ConfigTree
import requests

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
    CLUSTER_NAME_KEY = "cluster_name"
    DEFAULT_CONFIG = ConfigFactory.from_dict(
        {}
    )

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(KafkaSchemaRegistryExtractor.DEFAULT_CONFIG)

        self._registry_base_url = conf.get(
            KafkaSchemaRegistryExtractor.REGISTRY_URL_KEY
        )

        self._registry_username = conf.get(
            KafkaSchemaRegistryExtractor.REGISTRY_USERNAME_KEY
        )

        self._registry_password = conf.get(
            KafkaSchemaRegistryExtractor.REGISTRY_PASSWORD_KEY
        )

        self._cluster_name = conf.get(
            KafkaSchemaRegistryExtractor.CLUSTER_NAME_KEY
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

    def get_scope(self) -> str:
        return 'extractor.kafka_schema_registry'

    def _get_extract_iter(self):
        """
        Return an iterator generating TableMetadata for all of the schemas.
        """
        for subject in self._get_raw_extract_iter():
            LOGGER.info(f'Subject: {subject}')
            try:
                subject_schema = json.loads(subject['schema'])
                yield KafkaSchemaRegistryExtractor._create_table(
                    schema=subject_schema,
                    subject_name=subject['subject'],
                    cluster_name=self._cluster_name,
                    schema_name=subject_schema.get('name', ''),
                    schema_description=subject_schema.get('doc', ''),
                )
            except Exception as e:
                logger.warning(f'Failed to generate table for {subject}: {e}')
                continue

    def _get_raw_extract_iter(self) -> Iterator[Dict[str, Any]]:
        """
        Return iterator of results row from schema registry
        """
        subjects = self._get_all_subjects()

        LOGGER.info(f'Number of extracted subjects: {len(subjects)}')
        LOGGER.info(f'Extracted subjects: {subjects}')

        for subj in subjects:
            LOGGER.info(f'Getting subject: {subj}')
            max_version = \
                self._get_subject_max_version(
                    subj
                )
            LOGGER.info(f'Maximum version for subject {subj} is: {max_version}')

            yield self._get_subject(
                subj,
                max_version,
            )

    def _get_subject(self,
                     subject: str,
                     version: str) -> Dict[str, Any]:
        """
        Return the schema of the given subject
        """
        url = \
            f'{self._registry_base_url}/subjects/{subject}/versions/{version}'

        return requests.get(url).json()

    def _get_all_subjects(self) -> List[str]:
        """
        Return all subjects from Kafka Schema registry
        """
        url = f'{self._registry_base_url}/subjects'
        return requests.get(url).json()

    def _get_subject_max_version(self, subject: str) -> str:
        """
        Return maximum version of given subject
        """
        url = f'{self._registry_base_url}/subjects/{subject}/versions'

        return max(requests.get(url).json())

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
                    description=schema.get('doc', ''),
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
