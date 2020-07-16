# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional  # noqa: F401

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class DashboardESDocument(ElasticsearchDocument):
    """
    Schema for the ES dashboard ES document
    """

    def __init__(self,
                 group_name,  # type: str
                 name,  # type: str
                 description,  # type: Union[str, None]
                 total_usage,  # type: int
                 product='',  # type: Optional[str]
                 cluster='',  # type: Optional[str]
                 group_description=None,  # type: Optional[str]
                 query_names=None,  # type:  Union[List[str], None]
                 group_url=None,  # type: Optional[str]
                 url=None,  # type: Optional[str]
                 uri=None,  # type: Optional[str]
                 last_successful_run_timestamp=None,  # type: Optional[int]
                 tags=None,  # type: Optional[list[str]]
                 badges=None,  # type: Optional[list[str]]
                 ):
        # type: (...) -> None
        self.group_name = group_name
        self.name = name
        self.description = description
        self.cluster = cluster
        self.product = product
        self.group_url = group_url
        self.url = url
        self.uri = uri
        self.last_successful_run_timestamp = last_successful_run_timestamp
        self.total_usage = total_usage
        self.group_description = group_description
        self.query_names = query_names
        self.tags = tags
        self.badges = badges
