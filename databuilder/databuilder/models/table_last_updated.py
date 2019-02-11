from typing import Any, Dict, List, Union  # noqa: F401

from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable, NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE

from databuilder.models.table_metadata import TableMetadata


class TableLastUpdated(Neo4jCsvSerializable):
    # constants
    LAST_UPDATED_NODE_LABEL = 'Timestamp'
    LAST_UPDATED_KEY_FORMAT = '{db}://{cluster}.{schema}/{tbl}/timestamp'
    TIMESTAMP_PROPERTY = 'last_updated_timestamp'
    TIMESTAMP_NAME_PROPERTY = 'name'

    TABLE_LASTUPDATED_RELATION_TYPE = 'LAST_UPDATED_AT'
    LASTUPDATED_TABLE_RELATION_TYPE = 'LAST_UPDATED_TIME_OF'

    def __init__(self,
                 table_name,  # type: str
                 last_updated_time_epoch,  # type: int
                 schema_name,  # type: str
                 db='hive',  # type: str
                 cluster='gold'  # type: str
                 ):
        # type: (...) -> None
        self.table_name = table_name
        self.last_updated_time = int(last_updated_time_epoch)
        self.schema = schema_name
        self.db = db
        self.cluster = cluster

        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def __repr__(self):
        # type: (...) -> str
        return \
            """TableLastUpdated(table_name={!r}, last_updated_time={!r}, schema_name={!r}, db={!r}, cluster={!r})"""\
            .format(self.table_name, self.last_updated_time, self.schema, self.db, self.cluster)

    def create_next_node(self):
        # type: (...) -> Union[Dict[str, Any], None]
        # creates new node
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

    def get_table_model_key(self):
        # type: (...) -> str
        # returns formatted string for table name
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.db,
                                                     cluster=self.cluster,
                                                     schema=self.schema,
                                                     tbl=self.table_name)

    def get_last_updated_model_key(self):
        # type: (...) -> str
        # returns formatted string for last updated name
        return TableLastUpdated.LAST_UPDATED_KEY_FORMAT.format(db=self.db,
                                                               cluster=self.cluster,
                                                               schema=self.schema,
                                                               tbl=self.table_name)

    def create_nodes(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of Neo4j node records
        :return:
        """
        results = []

        results.append({
            NODE_KEY: self.get_last_updated_model_key(),
            NODE_LABEL: TableLastUpdated.LAST_UPDATED_NODE_LABEL,
            TableLastUpdated.TIMESTAMP_PROPERTY: self.last_updated_time,
            TableLastUpdated.TIMESTAMP_NAME_PROPERTY: TableLastUpdated.TIMESTAMP_PROPERTY
        })

        return results

    def create_relation(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of relations mapping last updated node with table node
        :return:
        """
        results = [{
            RELATION_START_KEY: self.get_table_model_key(),
            RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
            RELATION_END_KEY: self.get_last_updated_model_key(),
            RELATION_END_LABEL: TableLastUpdated.LAST_UPDATED_NODE_LABEL,
            RELATION_TYPE: TableLastUpdated.TABLE_LASTUPDATED_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableLastUpdated.LASTUPDATED_TABLE_RELATION_TYPE
        }]

        return results
