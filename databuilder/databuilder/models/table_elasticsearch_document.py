import json
from typing import List, Optional  # noqa: F401

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class TableESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document
    """
    def __init__(self,
                 elasticsearch_index,  # type: str
                 elasticsearch_type,   # type: str
                 database,  # type: str
                 cluster,  # type: str
                 schema_name,  # type: str
                 table_name,  # type: str
                 table_key,  # type: str
                 table_description,  # type: str
                 table_last_updated_epoch,  # type: Optional[int]
                 column_names,  # type: List[str]
                 column_descriptions,  # type: List[str]
                 total_usage,  # type: int
                 unique_usage,  # type: int
                 tag_names,  # type: List[str]
                 ):
        # type: (...) -> None
        self.elasticsearch_index = elasticsearch_index
        self.elasticsearch_type = elasticsearch_type
        self.database = database
        self.cluster = cluster
        self.schema_name = schema_name
        self.table_name = table_name
        self.table_key = table_key
        self.table_description = table_description
        self.table_last_updated_epoch = table_last_updated_epoch
        self.column_names = column_names
        self.column_descriptions = column_descriptions
        self.total_usage = total_usage
        self.unique_usage = unique_usage
        # todo: will include tag_type once we have better understanding from UI flow.
        self.tag_names = tag_names

    def to_json(self):
        # type: () -> str
        """
        Convert object to json for elasticsearch bulk upload
        Bulk load JSON format is defined here:
        https://www.elastic.co/guide/en/elasticsearch/reference/6.2/docs-bulk.html
        :return:
        """
        index_row = dict(index=dict(_index=self.elasticsearch_index,
                                    _type=self.elasticsearch_type))
        data = json.dumps(index_row) + "\n"

        # convert rest of the object
        obj_dict = {k: v for k, v in sorted(self.__dict__.items())
                    if k not in ['elasticsearch_index', 'elasticsearch_type']}
        data += json.dumps(obj_dict) + "\n"

        return data
