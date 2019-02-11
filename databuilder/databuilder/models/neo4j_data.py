from typing import List, Optional  # noqa: F401


class Neo4jDataResult:
    """
    Neo4j Graph data model
    CYPHER QUERY returns one column per row
    """
    def __init__(self,
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
        self.database = database
        self.cluster = cluster
        self.schema_name = schema_name
        self.table_name = table_name
        self.table_key = table_key
        self.table_description = table_description
        self.table_last_updated_epoch = int(table_last_updated_epoch) if table_last_updated_epoch else None
        self.column_names = column_names
        self.column_descriptions = column_descriptions
        self.total_usage = total_usage
        self.unique_usage = unique_usage
        self.tag_names = tag_names
