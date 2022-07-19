# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
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

        self._extract_iter: Union[None, Iterator] = None

    def extract(self) -> Union[TableMetadata, None]:
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def get_scope(self) -> str:
        return 'extractor.kafka_schema_registry'

    def _get_extract_iter():
        pass

    def _get_raw_extract_iter(self) -> Iterator[Dict[str, Any]]:
        """
        Return iterator of results row from schema registry
        """
        subjects = KafkaSchemaRegistryExtractor._get_all_subjects()

        for subj in subjects:
            max_version = \
                KafkaSchemaRegistryExtractor._get_subject_max_version(
                    subj
                )

            yield KafkaSchemaRegistryExtractor._get_schema(
                subj,
                max_version,
            )

    def _get_schema(self,
                    subject: str,
                    version: str) -> Dict[str, Any]:
        """
        Return the schema of the given subject
        """
        url = \
            f'{self._registry_base_url}/subjects/{subject}/versions/{version}'

        try:
            req_res = requests.get(url).json()
        except Exception as e:
            LOGGER.error(
                f'failed to get schema from {url}: {e}'
            )
            raise

        try:
            res = json.loads(req_res['schema'])
        except Exception as e:
            LOGGER.error(
                f'failed to convert schema {req_res["schema"]} to json: {e}'
            )

        return res

    def _get_all_subjects(self) -> List[str]:
        """
        Return all subjects from Kafka Schema registry
        """
        url = f'{self._registry_base_url}/subjects'

        try:
            res = requests.get(url).json()
        except Exception as e:
            LOGGER.error(
                f'failed to get subjects from {url}: {e}'
            )
            raise

        return res

    def _get_subject_max_version(self, subject: str) -> str:
        """
        Return maximum version of given subject
        """
        url = f'{self._registry_base_url}/subjects/{subject}/versions'

        try:
            res = requests.get(url).json()
        except Exception as e:
            LOGGER.error(
                f'failed to get subject {subject} versions from {url}: {e}'
            )
            raise

        return max(res)
