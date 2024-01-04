# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class DataProviderESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document
    """

    def __init__(self,
                 name: str,
                 key: str,
                 description: str,
                 last_updated_timestamp: Optional[int],
                 data_channel_names: List[str],
                 data_channel_types: List[str],
                 data_channel_descriptions: List[str],
                 data_location_names: List[str],
                 data_location_types: List[str],
                #  tags: List[str],
                #  badges: Optional[List[str]] = None,
                 ) -> None:
        self.name = name
        self.key = key
        self.description = description
        self.last_updated_timestamp = int(last_updated_timestamp) if last_updated_timestamp else None
        self.data_channel_names = data_channel_names
        self.data_channel_types = data_channel_types
        self.data_channel_descriptions = data_channel_descriptions
        self.data_location_names = data_location_names
        self.data_location_types = data_location_types
        # self.tags = tags
        # self.badges = badges
