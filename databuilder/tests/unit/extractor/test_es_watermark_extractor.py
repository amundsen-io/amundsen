# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from datetime import datetime
from typing import (
    Any, Dict, List,
)

from pyhocon import ConfigFactory

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.es_watermark_extractor import ElasticsearchWatermarkExtractor
from databuilder.models.watermark import Watermark


class TestElasticsearchWatermarkBlizzExtractor(unittest.TestCase):
    # Index names
    index_with_no_data = 'index_with_no_data'
    index_with_data_1 = 'index_with_data_1'
    index_with_data_2 = 'index_with_data_2'

    # Meta
    indices_meta = {
        index_with_no_data: {
            'settings': {
                'index': {
                    'creation_date': '1641861298000'
                }
            }
        },
        index_with_data_1: {
            'settings': {
                'index': {
                    'creation_date': '1641863003000'
                }
            }
        },
        index_with_data_2: {
            'settings': {
                'index': {
                    'creation_date': '1641949455000'
                }
            }
        }
    }

    # Watermarks
    indices_watermarks = {
        index_with_no_data: {
            'aggregations': {
                'min_watermark': {
                    'value': None
                },
                'max_watermark': {
                    'value': None
                }
            }
        },
        index_with_data_1: {
            'aggregations': {
                'min_watermark': {
                    'value': 1641863055000
                },
                'max_watermark': {
                    'value': 1641949455000
                }
            }
        },
        index_with_data_2: {
            'aggregations': {
                'min_watermark': {
                    'value': 1641949455000
                },
                'max_watermark': {
                    'value': 1642126450000
                }
            }
        }
    }

    class MockElasticsearch:
        def __init__(self, indices: Dict, indices_watermarks: Dict) -> None:
            self.indices = {'*': indices}
            self.indices_watermarks = indices_watermarks

        def search(self, index: str, size: int, aggs: Dict) -> Any:
            return self.indices_watermarks[index]

    def _get_indices_meta(self, index_names: List[str]) -> Dict:
        indices_meta = {}
        for index_name in index_names:
            indices_meta[index_name] = self.indices_meta[index_name]

        return indices_meta

    def _get_config(self, index_names: List[str]) -> Any:
        return ConfigFactory.from_dict({
            'extractor.es_watermark.schema': 'schema_name',
            'extractor.es_watermark.cluster': 'cluster_name',
            'extractor.es_watermark.time_field': 'time',
            'extractor.es_watermark.client': self.MockElasticsearch(
                self._get_indices_meta(index_names),
                self.indices_watermarks
            )})

    def _get_extractor(self, index_names: List[str]) -> Any:
        extractor = ElasticsearchWatermarkExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=self._get_config(index_names), scope=extractor.get_scope()))

        return extractor

    def _extract_and_compare(self, extractor: Extractor, expected: List[Watermark]) -> None:
        result = []

        while True:
            entry = extractor.extract()
            if entry:
                result.append(entry)
            else:
                break

        self.assertEqual(len(expected), len(result))
        for idx in range(len(expected)):
            self.assertEqual(expected[idx].__repr__(), result[idx].__repr__())

    def test_no_indices(self) -> None:
        extractor = self._get_extractor([])
        expected: List[Watermark] = []
        self._extract_and_compare(extractor, expected)

    def test_index_with_no_data(self) -> None:
        extractor = self._get_extractor([self.index_with_no_data])
        expected: List[Watermark] = []
        self._extract_and_compare(extractor, expected)

    def test_index_with_data(self) -> None:
        extractor = self._get_extractor([self.index_with_data_1])
        expected = [
            Watermark(
                database='elasticsearch',
                cluster='cluster_name',
                schema='schema_name',
                table_name='index_with_data_1',
                create_time=datetime.fromtimestamp(1641863003).strftime('%Y-%m-%d %H:%M:%S'),
                part_name=f"time={datetime.fromtimestamp(1641863055).strftime('%Y-%m-%d')}",
                part_type='low_watermark'
            ),
            Watermark(
                database='elasticsearch',
                cluster='cluster_name',
                schema='schema_name',
                table_name='index_with_data_1',
                create_time=datetime.fromtimestamp(1641863003).strftime('%Y-%m-%d %H:%M:%S'),
                part_name=f"time={datetime.fromtimestamp(1641949455).strftime('%Y-%m-%d')}",
                part_type='high_watermark'
            )
        ]
        self._extract_and_compare(extractor, expected)

    def test_indices_with_and_without_data(self) -> None:
        extractor = self._get_extractor([self.index_with_no_data, self.index_with_data_1, self.index_with_data_2])
        expected = [
            Watermark(
                database='elasticsearch',
                cluster='cluster_name',
                schema='schema_name',
                table_name='index_with_data_1',
                create_time=datetime.fromtimestamp(1641863003).strftime('%Y-%m-%d %H:%M:%S'),
                part_name=f"time={datetime.fromtimestamp(1641863055).strftime('%Y-%m-%d')}",
                part_type='low_watermark'
            ),
            Watermark(
                database='elasticsearch',
                cluster='cluster_name',
                schema='schema_name',
                table_name='index_with_data_1',
                create_time=datetime.fromtimestamp(1641863003).strftime('%Y-%m-%d %H:%M:%S'),
                part_name=f"time={datetime.fromtimestamp(1641949455).strftime('%Y-%m-%d')}",
                part_type='high_watermark'
            ),
            Watermark(
                database='elasticsearch',
                cluster='cluster_name',
                schema='schema_name',
                table_name='index_with_data_2',
                create_time=datetime.fromtimestamp(1641949455).strftime('%Y-%m-%d %H:%M:%S'),
                part_name=f"time={datetime.fromtimestamp(1641949455).strftime('%Y-%m-%d')}",
                part_type='low_watermark'
            ),
            Watermark(
                database='elasticsearch',
                cluster='cluster_name',
                schema='schema_name',
                table_name='index_with_data_2',
                create_time=datetime.fromtimestamp(1641949455).strftime('%Y-%m-%d %H:%M:%S'),
                part_name=f"time={datetime.fromtimestamp(1642126450).strftime('%Y-%m-%d')}",
                part_type='high_watermark'
            )
        ]
        self._extract_and_compare(extractor, expected)
