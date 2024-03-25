# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
import json
from typing import (
    Dict, Iterator, Optional, Union,
)

from databuilder.extractor.es_base_extractor import ElasticsearchBaseExtractor
from databuilder.models.table_metadata import TableMetadata


class ElasticsearchMetadataExtractor(ElasticsearchBaseExtractor):
    """
    Extractor to extract index metadata from Elasticsearch
    """

    def get_scope(self) -> str:
        return 'extractor.es_metadata'

    def _render_programmatic_description(self, input: Optional[Dict]) -> Optional[str]:
        if input:
            result = f"""```\n{json.dumps(input, indent=2)}\n```"""

            return result
        else:
            return None

    def _get_extract_iter(self) -> Iterator[Union[TableMetadata, None]]:
        indexes: Dict = self._get_indexes()

        for index_name, index_metadata in indexes.items():
            properties = self._get_index_mapping_properties(index_metadata) or dict()

            columns = self._get_attributes(input_mapping=properties)

            # The columns are already sorted, but the sort_order needs to be added to each column metadata entry
            if self._correct_sort_order:
                for index in range(len(columns)):
                    columns[index].sort_order = index

            table_metadata = TableMetadata(database=self.database,
                                           cluster=self.cluster,
                                           schema=self.schema,
                                           name=index_name,
                                           description=None,
                                           columns=columns,
                                           is_view=False,
                                           tags=None,
                                           description_source=None)

            yield table_metadata

            if self._extract_technical_details:
                _settings = index_metadata.get('settings', dict())
                _aliases = index_metadata.get('aliases', dict())

                settings = self._render_programmatic_description(_settings)
                aliases = self._render_programmatic_description(_aliases)

                if aliases:
                    yield TableMetadata(database=self.database,
                                        cluster=self.cluster,
                                        schema=self.schema,
                                        name=index_name,
                                        description=aliases,
                                        columns=columns,
                                        is_view=False,
                                        tags=None,
                                        description_source='aliases')
                if settings:
                    yield TableMetadata(database=self.database,
                                        cluster=self.cluster,
                                        schema=self.schema,
                                        name=index_name,
                                        description=settings,
                                        columns=columns,
                                        is_view=False,
                                        tags=None,
                                        description_source='settings')
