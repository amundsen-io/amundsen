# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
import abc
from typing import (
    Any, Dict, Iterator, Optional, Union, List,
)

from pyhocon import ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_metadata import ColumnMetadata


class ElasticsearchBaseExtractor(Extractor):
    """
    Extractor to extract index metadata from Elasticsearch

    By default, the extractor does not extract nested columns. Set ELASTICSEARCH_EXTRACT_NESTED_COLUMNS conf to True
    to have nested columns extracted.

    By default, the extractor does not add sort_order to columns. Set ELASTICSEARCH_CORRECT_SORT_ORDER conf to True
    for columns to have correct sort order.
    """

    ELASTICSEARCH_CLIENT_CONFIG_KEY = 'client'
    ELASTICSEARCH_EXTRACT_TECHNICAL_DETAILS = 'extract_technical_details'

    # For backwards compatibility, the Elasticsearch extractor does not extract nested columns by default.
    # Set this to true in the conf to have nested columns extracted.
    ELASTICSEARCH_EXTRACT_NESTED_COLUMNS = 'extract_nested_columns'

    # For backwards compatibility, the Elasticsearch extractor does not add sort_order to columns by default.
    # Set this to true in the conf for columns to have correct sort order.
    ELASTICSEARCH_CORRECT_SORT_ORDER = 'correct_sort_order'

    CLUSTER = 'cluster'
    SCHEMA = 'schema'

    def __init__(self) -> None:
        super(ElasticsearchBaseExtractor, self).__init__()

    def init(self, conf: ConfigTree) -> None:
        self.conf = conf
        self._extract_iter = self._get_extract_iter()

        self.es = self.conf.get(ElasticsearchBaseExtractor.ELASTICSEARCH_CLIENT_CONFIG_KEY)

    def _get_es_version(self) -> Optional[str]:
        version = ''

        try:
            info = self.es.info()
            if info:
                version = info.get('version').get('number')
        except Exception:
            pass

        return version

    def _get_indexes(self) -> Dict:
        result = dict()

        try:
            _indexes = self.es.indices.get('*')

            for k, v in _indexes.items():
                if not k.startswith('.'):
                    result[k] = v
        except Exception:
            pass

        return result

    def _get_index_mapping_properties(self, index: Dict) -> Optional[Dict]:
        mappings = index.get('mappings', dict())

        # Mapping types were removed in Elasticsearch 7. As a result, index mappings are formatted differently.
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/removal-of-types.html
        no_mapping_types = False
        version = self._get_es_version()
        if len(version) > 0:
            version_numbers = version.split('.')
            if int(version_numbers[0]) >= 7:
                no_mapping_types = True

        try:
            if no_mapping_types:
                properties = mappings.get('properties', dict())
            else:
                properties = list(mappings.values())[0].get('properties', dict())
        except Exception:
            properties = dict()

        return properties

    def _get_nested_columns(self,
                            input_mapping: Dict,
                            parent_col_name: bool = False,
                            separator: str = '.') -> List[ColumnMetadata]:
        cols: List[ColumnMetadata] = []

        for col_name, col_mapping in input_mapping.items():
            qualified_col_name = str(parent_col_name) + separator + col_name if parent_col_name else col_name
            if isinstance(col_mapping, dict):
                if col_mapping.__contains__('properties'):
                    # Need to recurse
                    cols.extend(self._get_nested_columns(input_mapping=col_mapping.get('properties'),
                                                         parent_col_name=qualified_col_name,
                                                         separator=separator))
                else:
                    cols.append(ColumnMetadata(name=qualified_col_name,
                                               description='',
                                               col_type=col_mapping.get('type', ''),
                                               sort_order=0))

        return cols

    def extract(self) -> Any:
        try:
            result = next(self._extract_iter)

            return result
        except StopIteration:
            return None

    @property
    def database(self) -> str:
        return 'elasticsearch'

    @property
    def cluster(self) -> str:
        return self.conf.get(ElasticsearchBaseExtractor.CLUSTER)

    @property
    def schema(self) -> str:
        return self.conf.get(ElasticsearchBaseExtractor.SCHEMA)

    @property
    def _extract_technical_details(self) -> bool:
        try:
            return self.conf.get(ElasticsearchBaseExtractor.ELASTICSEARCH_EXTRACT_TECHNICAL_DETAILS)
        except Exception:
            return False

    @property
    def _extract_nested_columns(self) -> bool:
        try:
            return self.conf.get(ElasticsearchBaseExtractor.ELASTICSEARCH_EXTRACT_NESTED_COLUMNS)
        except Exception:
            return False

    @property
    def _correct_sort_order(self) -> bool:
        try:
            return self.conf.get(ElasticsearchBaseExtractor.ELASTICSEARCH_CORRECT_SORT_ORDER)
        except Exception:
            return False

    @abc.abstractmethod
    def _get_extract_iter(self) -> Iterator[Union[Any, None]]:
        pass
