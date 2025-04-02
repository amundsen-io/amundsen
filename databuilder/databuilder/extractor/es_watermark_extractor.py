# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import (
    Dict, Iterator, Optional, Tuple, Union,
)

from databuilder.extractor.es_base_extractor import ElasticsearchBaseExtractor
from databuilder.models.watermark import Watermark


class ElasticsearchWatermarkExtractor(ElasticsearchBaseExtractor):
    """
    Extractor to extract index watermarks from Elasticsearch
    """

    def get_scope(self) -> str:
        return 'extractor.es_watermark'

    # Internally, Elasticsearch stores dates as numbers representing milliseconds since the epoch,
    # so the agg result is expected to be floats.
    # See https://www.elastic.co/guide/en/elasticsearch/reference/current/date.html#date
    def _get_index_watermark_bounds(self, index_name: str) -> Optional[Tuple[float, float]]:
        try:
            search_result = self.es.search(
                index=index_name,
                size=0,
                aggs={
                    'min_watermark': {'min': {'field': self._time_field}},
                    'max_watermark': {'max': {'field': self._time_field}}
                }
            )
            watermark_min = search_result.get('aggregations').get('min_watermark').get('value')
            watermark_max = search_result.get('aggregations').get('max_watermark').get('value')
            if watermark_min is not None and watermark_max is not None:
                return float(watermark_min), float(watermark_max)
        except Exception:
            pass

        return None

    def _get_extract_iter(self) -> Iterator[Union[Watermark, None]]:
        # Get all the indices
        indices: Dict = self._get_indexes()

        # Iterate over indices
        for index_name, index_metadata in indices.items():
            creation_date: Optional[float] = self._get_index_creation_date(index_metadata)
            watermark_bounds: Optional[Tuple[float, float]] = self._get_index_watermark_bounds(index_name=index_name)
            watermark_min: Optional[float] = None if watermark_bounds is None else watermark_bounds[0]
            watermark_max: Optional[float] = None if watermark_bounds is None else watermark_bounds[1]

            if creation_date is None or watermark_min is None or watermark_max is None:
                continue

            creation_date_str: str = datetime.fromtimestamp(creation_date / 1000).strftime('%Y-%m-%d %H:%M:%S')
            watermark_min_str: str = datetime.fromtimestamp(watermark_min / 1000).strftime('%Y-%m-%d')
            watermark_max_str: str = datetime.fromtimestamp(watermark_max / 1000).strftime('%Y-%m-%d')

            yield Watermark(
                database=self.database,
                cluster=self.cluster,
                schema=self.schema,
                table_name=index_name,
                create_time=creation_date_str,
                part_name=f'{self._time_field}={watermark_min_str}',
                part_type='low_watermark'
            )

            yield Watermark(
                database=self.database,
                cluster=self.cluster,
                schema=self.schema,
                table_name=index_name,
                create_time=creation_date_str,
                part_name=f'{self._time_field}={watermark_max_str}',
                part_type='high_watermark'
            )
