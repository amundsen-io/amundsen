from typing import Any, Dict, List, Union  # noqa: F401

from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable, NODE_KEY, \
    NODE_LABEL


class TestTableModel(Neo4jCsvSerializable):
    # type: (...) -> None
    """
    Hive table watermark result model.
    Each instance represents one row of hive watermark result.
    """
    LABEL = 'Table'
    KEY_FORMAT = '{db}://{cluster}.{schema}/{ tbl}'

    def __init__(self,
                 database,  # type: str
                 cluster,  # type: str
                 schema_name,  # type: str
                 table_name,  # type: str
                 table_desc,  # type: str
                 ):
        # type: (...) -> None
        self.database = database
        self.cluster = cluster
        self.schema_name = schema_name
        self.table_name = table_name
        self.table_desc = table_desc

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

    def create_nodes(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of Neo4j node records
        :return:
        """
        results = []

        results.append({
            NODE_KEY: '{db}://{cluster}.{schema}/{tbl}'.format(db=self.database,
                                                               cluster=self.cluster,
                                                               schema=self.schema_name,
                                                               tbl=self.table_name),
            NODE_LABEL: TestTableModel.LABEL,
            'table_desc': self.table_desc,
            'tbl_key': '{db}://{cluster}.{schema}/{tbl}'.format(db=self.database,
                                                                cluster=self.cluster,
                                                                schema=self.schema_name,
                                                                tbl=self.table_name)
        })
        return results

    def create_relation(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of relation map between watermark record with original hive table
        :return:
        """
        return []
