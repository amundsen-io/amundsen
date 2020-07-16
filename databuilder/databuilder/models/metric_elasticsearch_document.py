# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional  # noqa: F401

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class MetricESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document
    """

    def __init__(self,
                 name,  # type: str
                 description,  # type: str
                 type,  # type: str
                 dashboards,  # type: List
                 tags,  # type: List
                 ):
        # type: (...) -> None
        self.name = name
        self.description = description
        self.type = type
        self.dashboards = dashboards
        self.tags = tags
