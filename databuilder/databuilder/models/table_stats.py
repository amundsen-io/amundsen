# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, Union  # noqa: F401

from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable, NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE
from databuilder.models.table_metadata import ColumnMetadata


class TableColumnStats(Neo4jCsvSerializable):
    # type: (...) -> None
    """
    Hive table stats model.
    Each instance represents one row of hive watermark result.
    """
    LABEL = 'Stat'
    KEY_FORMAT = '{db}://{cluster}.{schema}' \
                 '/{table}/{col}/{stat_name}/'
    STAT_Column_RELATION_TYPE = 'STAT_OF'
    Column_STAT_RELATION_TYPE = 'STAT'

    def __init__(self,
                 table_name,  # type: str
                 col_name,  # type: str
                 stat_name,  # type: str
                 stat_val,  # type: str
                 start_epoch,  # type: str
                 end_epoch,  # type: str
                 db='hive',  # type: str
                 cluster='gold',  # type: str
                 schema=None  # type: str
                 ):
        # type: (...) -> None
        if schema is None:
            self.schema, self.table = table_name.split('.')
        else:
            self.table = table_name.lower()
            self.schema = schema.lower()
        self.db = db
        self.col_name = col_name.lower()
        self.start_epoch = start_epoch
        self.end_epoch = end_epoch
        self.cluster = cluster
        self.stat_name = stat_name
        self.stat_val = stat_val
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

    def get_table_stat_model_key(self):
        # type: (...) -> str
        return TableColumnStats.KEY_FORMAT.format(db=self.db,
                                                  cluster=self.cluster,
                                                  schema=self.schema,
                                                  table=self.table,
                                                  col=self.col_name,
                                                  stat_name=self.stat_name)

    def get_col_key(self):
        # type: (...) -> str
        # no cluster, schema info from the input
        return ColumnMetadata.COLUMN_KEY_FORMAT.format(db=self.db,
                                                       cluster=self.cluster,
                                                       schema=self.schema,
                                                       tbl=self.table,
                                                       col=self.col_name)

    def create_nodes(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of Neo4j node records
        :return:
        """
        results = [{
            NODE_KEY: self.get_table_stat_model_key(),
            NODE_LABEL: TableColumnStats.LABEL,
            'stat_val:UNQUOTED': self.stat_val,
            'stat_name': self.stat_name,
            'start_epoch': self.start_epoch,
            'end_epoch': self.end_epoch,
        }]
        return results

    def create_relation(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of relation map between table stat record with original hive table
        :return:
        """
        results = [{
            RELATION_START_KEY: self.get_table_stat_model_key(),
            RELATION_START_LABEL: TableColumnStats.LABEL,
            RELATION_END_KEY: self.get_col_key(),
            RELATION_END_LABEL: ColumnMetadata.COLUMN_NODE_LABEL,
            RELATION_TYPE: TableColumnStats.STAT_Column_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableColumnStats.Column_STAT_RELATION_TYPE
        }]
        return results
