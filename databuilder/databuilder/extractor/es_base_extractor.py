# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
import abc
from typing import (
    Any, Dict, Iterator, List, Optional, Union,
)

from pyhocon import ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_metadata import ColumnMetadata


class ElasticsearchBaseExtractor(Extractor):
    """
    Extractor to extract index metadata from Elasticsearch

    By default, the extractor does not add sort_order to columns. Set ELASTICSEARCH_CORRECT_SORT_ORDER conf to True
    for columns to have correct sort order.

    Set ELASTICSEARCH_TIME_FIELD to the name of the field representing time.
    """

    ELASTICSEARCH_CLIENT_CONFIG_KEY = 'client'
    ELASTICSEARCH_EXTRACT_TECHNICAL_DETAILS = 'extract_technical_details'

    # For backwards compatibility, the Elasticsearch extractor does not add sort_order to columns by default.
    # Set this to true in the conf for columns to have correct sort order.
    ELASTICSEARCH_CORRECT_SORT_ORDER = 'correct_sort_order'

    # Set this to the name of the field representing time.
    ELASTICSEARCH_TIME_FIELD = 'time_field'

    CLUSTER = 'cluster'
    SCHEMA = 'schema'

    def __init__(self) -> None:
        super(ElasticsearchBaseExtractor, self).__init__()

    def init(self, conf: ConfigTree) -> None:
        self.conf = conf
        self._extract_iter = self._get_extract_iter()

        self.es = self.conf.get(ElasticsearchBaseExtractor.ELASTICSEARCH_CLIENT_CONFIG_KEY)

    def _get_es_version(self) -> str:
        return self.es.info().get('version').get('number')

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

    def _get_index_creation_date(self, index_metadata: Dict) -> Optional[float]:
        try:
            return float(index_metadata.get('settings', dict()).get('index').get('creation_date'))
        except Exception:
            return None

    def _get_index_mapping_properties(self, index: Dict) -> Optional[Dict]:
        mappings = index.get('mappings', dict())

        # Mapping types were removed in Elasticsearch 7. As a result, index mappings are formatted differently.
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/removal-of-types.html
        version = self._get_es_version()

        try:
            if int(version.split('.')[0]) >= 7:
                properties = mappings.get('properties', dict())
            else:
                properties = list(mappings.values())[0].get('properties', dict())
        except Exception:
            properties = dict()

        return properties

    def _get_attributes(self,
                        input_mapping: Dict,
                        parent_col_name: str = '',
                        separator: str = '.') -> List[ColumnMetadata]:
        cols: List[ColumnMetadata] = []

        for col_name, col_mapping in input_mapping.items():
            qualified_col_name = str(parent_col_name) + separator + col_name if parent_col_name else col_name
            if isinstance(col_mapping, dict):
                if col_mapping.__contains__('properties'):
                    # Need to recurse
                    inner_mapping: Dict = col_mapping.get('properties', {})
                    cols.extend(self._get_attributes(input_mapping=inner_mapping,
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
    def _correct_sort_order(self) -> bool:
        try:
            return self.conf.get(ElasticsearchBaseExtractor.ELASTICSEARCH_CORRECT_SORT_ORDER)
        except Exception:
            return False

    # Default time field is @timestamp to match ECS
    # See https://www.elastic.co/guide/en/ecs/master/ecs-base.html
    @property
    def _time_field(self) -> str:
        return self.conf.get(ElasticsearchBaseExtractor.ELASTICSEARCH_TIME_FIELD, '@timestamp')

    @abc.abstractmethod
    def _get_extract_iter(self) -> Iterator[Union[Any, None]]:
        pass
