from typing import List, Optional  # noqa: F401

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class TableESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document
    """
    def __init__(self,
                 database,  # type: str
                 cluster,  # type: str
                 schema_name,  # type: str
                 name,  # type: str
                 key,  # type: str
                 description,  # type: str
                 last_updated_epoch,  # type: Optional[int]
                 column_names,  # type: List[str]
                 column_descriptions,  # type: List[str]
                 total_usage,  # type: int
                 unique_usage,  # type: int
                 tags,  # type: List[str]
                 display_name=None,  # type: Optional[str]
                 ):
        # type: (...) -> None
        self.database = database
        self.cluster = cluster
        self.schema_name = schema_name
        self.name = name
        self.display_name = display_name if display_name else '{schema}.{table}'.format(schema=schema_name, table=name)
        self.key = key
        self.description = description
        # todo: use last_updated_timestamp to match the record in metadata
        self.last_updated_epoch = int(last_updated_epoch) if last_updated_epoch else None
        self.column_names = column_names
        self.column_descriptions = column_descriptions
        self.total_usage = total_usage
        self.unique_usage = unique_usage
        # todo: will include tag_type once we have better understanding from UI flow.
        self.tags = tags
