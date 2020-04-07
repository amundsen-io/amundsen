from typing import List, Optional  # noqa: F401

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class DashboardESDocument(ElasticsearchDocument):
    """
    Schema for the ES dashboard ES document
    """
    def __init__(self,
                 dashboard_group,  # type: str
                 dashboard_name,  # type: str
                 description,  # type: Union[str, None]
                 total_usage,  # type: int
                 product='',  # type: Optional[str]
                 cluster='',  # type: Optional[str]
                 dashboard_group_description=None,  # type: Optional[str]
                 query_names=None,  # type:  Union[List[str], None]
                 group_url=None,  # type: Optional[str]
                 url=None,  # type: Optional[str]
                 uri=None,  # type: Optional[str]
                 last_successful_run_timestamp=None,  # type: Optional[int]
                 tags=None  # type: list
                 ):
        # type: (...) -> None
        self.dashboard_group = dashboard_group
        self.dashboard_name = dashboard_name
        self.description = description
        self.cluster = cluster
        self.product = product
        self.group_url = group_url
        self.url = url
        self.uri = uri
        self.last_successful_run_timestamp = last_successful_run_timestamp
        self.total_usage = total_usage
        self.dashboard_group_description = dashboard_group_description
        self.query_names = query_names
        self.tags = tags
