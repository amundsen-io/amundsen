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
                 dashboard_group_description=None,  # type: Optional[str]
                 tags=None  # type: list
                 ):
        # type: (...) -> None
        self.dashboard_group = dashboard_group
        self.dashboard_name = dashboard_name
        self.description = description
        self.product = product
        self.total_usage = total_usage
        self.dashboard_group_description = dashboard_group_description
        self.tags = tags
