# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class MetricESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document
    """

    def __init__(self,
                 name: str,
                 description: str,
                 type: str,
                 dashboards: List,
                 tags: List,
                 ) -> None:
        self.name = name
        self.description = description
        self.type = type
        self.dashboards = dashboards
        self.tags = tags
