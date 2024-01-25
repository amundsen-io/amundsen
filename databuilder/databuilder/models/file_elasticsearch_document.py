# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class FileESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document
    """

    def __init__(self,
                 name: str,
                 key: str,
                 description: str,
                 type: str,
                 path: str,
                 is_directory: bool,
                 data_channel_name: str,
                 data_location_name: str,
                 data_provider_name: str,
                 last_updated_timestamp: Optional[int],
                #  tags: List[str],
                #  badges: Optional[List[str]] = None,
                 ) -> None:
        self.name = name
        self.key = key
        self.description = description
        self.type = type
        self.path = path
        self.is_directory = is_directory
        self.last_updated_timestamp = int(last_updated_timestamp) if last_updated_timestamp else None
        self.data_location_name = data_location_name
        self.data_channel_name = data_channel_name
        self.data_provider_name = data_provider_name
        # self.tags = tags
        # self.badges = badges
