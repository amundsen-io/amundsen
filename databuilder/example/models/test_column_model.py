from typing import Any, Dict, List, Union  # noqa: F401

from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, NODE_LABEL, NODE_KEY, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)

from databuilder.models.table_metadata import TableMetadata


class TestColumnMetadata(Neo4jCsvSerializable):
    COLUMN_NODE_LABEL = 'Column'
    COLUMN_KEY_FORMAT = '{db}://{cluster}.{schema}/{tbl}/{col}'
    COLUMN_NAME = 'name'
    COLUMN_TYPE = 'type'
    COLUMN_ORDER = 'sort_order'
    COLUMN_DESCRIPTION = 'description'
    COLUMN_DESCRIPTION_FORMAT = '{db}://{cluster}.{schema}/{tbl}/{col}/_description'

    # pair of nodes makes relationship where name of variable represents order of relationship.
    COL_DESCRIPTION_RELATION_TYPE = 'DESCRIPTION'
    DESCRIPTION_COL_RELATION_TYPE = 'DESCRIPTION_OF'

    def __init__(self,
                 name,  # type: str
                 description,  # type: Union[str, None]
                 col_type,  # type: str
                 sort_order,  # type: int
                 database,  # type: str
                 cluster,  # type: str
                 schema_name,  # type: str
                 table_name,  # type: str
                 table_description,  # type: str
                 ):
        # type: (...) -> None
        """
        TODO: Add stats
        :param name:
        :param description:
        :param col_type:
        :param sort_order:
        """
        self.name = name
        self.description = description
        self.type = col_type
        self.sort_order = sort_order
        self.database = database
        self.cluster = cluster
        self.schema_name = schema_name
        self.table_name = table_name
        self.table_desc = table_description

        # currently we don't consider nested partitions
        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def create_next_node(self):
        # type: (...) -> Union[Dict[str, Any], None]
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self):
        # type: (...) -> Union[Dict[str, Any], None]
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def _get_col_key(self):
        # type: (TestColumnMetadata) -> str
        return TestColumnMetadata.COLUMN_KEY_FORMAT.format(db=self.database,
                                                           cluster=self.cluster,
                                                           schema=self.schema_name,
                                                           tbl=self.table_name,
                                                           col=self.name)

    def _get_table_key(self):
        # type: () -> str
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.database,
                                                     cluster=self.cluster,
                                                     schema=self.schema_name,
                                                     tbl=self.table_name)

    def create_nodes(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of Neo4j node records
        :return:
        """
        results = []

        results.append({
            NODE_LABEL: TestColumnMetadata.COLUMN_NODE_LABEL,
            NODE_KEY: self._get_col_key(),
            TestColumnMetadata.COLUMN_NAME: self.name,
            TestColumnMetadata.COLUMN_TYPE: self.type,
            TestColumnMetadata.COLUMN_ORDER: self.sort_order
        })
        return results

    def create_relation(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of relation map between watermark record with original hive table
        :return:
        """
        return [{
            RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
            RELATION_END_LABEL: TestColumnMetadata.COLUMN_NODE_LABEL,
            RELATION_START_KEY: self._get_table_key(),
            RELATION_END_KEY: self._get_col_key(),
            RELATION_TYPE: TableMetadata.TABLE_COL_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableMetadata.COL_TABLE_RELATION_TYPE
        }]

    def __repr__(self):
        # type: () -> str
        return 'ColumnMetadata({!r}, {!r}, {!r}, {!r})'.format(self.name,
                                                               self.description,
                                                               self.type,
                                                               self.sort_order)
