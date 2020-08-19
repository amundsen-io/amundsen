# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, Optional

from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable, NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE

from databuilder.models.table_metadata import TableMetadata


class TableSource(Neo4jCsvSerializable):
    """
    Hive table source model.
    """
    LABEL = 'Source'
    KEY_FORMAT = '{db}://{cluster}.{schema}/{tbl}/_source'
    SOURCE_TABLE_RELATION_TYPE = 'SOURCE_OF'
    TABLE_SOURCE_RELATION_TYPE = 'SOURCE'

    def __init__(self,
                 db_name: str,
                 schema: str,
                 table_name: str,
                 cluster: str,
                 source: str,
                 source_type: str='github',
                 ) -> None:
        self.db = db_name.lower()
        self.schema = schema.lower()
        self.table = table_name.lower()

        self.cluster = cluster.lower() if cluster else 'gold'
        # source is the source file location
        self.source = source
        self.source_type = source_type
        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def create_next_node(self) -> Optional[Dict[str, Any]]:
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[Dict[str, Any]]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def get_source_model_key(self) -> str:
        return TableSource.KEY_FORMAT.format(db=self.db,
                                             cluster=self.cluster,
                                             schema=self.schema,
                                             tbl=self.table)

    def get_metadata_model_key(self) -> str:
        return '{db}://{cluster}.{schema}/{table}'.format(db=self.db,
                                                          cluster=self.cluster,
                                                          schema=self.schema,
                                                          table=self.table)

    def create_nodes(self) -> List[Dict[str, Any]]:
        """
        Create a list of Neo4j node records
        :return:
        """
        results = [{
            NODE_KEY: self.get_source_model_key(),
            NODE_LABEL: TableSource.LABEL,
            'source': self.source,
            'source_type': self.source_type
        }]
        return results

    def create_relation(self) -> List[Dict[str, Any]]:
        """
        Create a list of relation map between owner record with original hive table
        :return:
        """
        results = [{
            RELATION_START_KEY: self.get_source_model_key(),
            RELATION_START_LABEL: TableSource.LABEL,
            RELATION_END_KEY: self.get_metadata_model_key(),
            RELATION_END_LABEL: TableMetadata.TABLE_NODE_LABEL,
            RELATION_TYPE: TableSource.SOURCE_TABLE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableSource.TABLE_SOURCE_RELATION_TYPE
        }]
        return results

    def __repr__(self) -> str:
        return 'TableSource({!r}, {!r}, {!r}, {!r}, {!r})'.format(self.db,
                                                                  self.cluster,
                                                                  self.schema,
                                                                  self.table,
                                                                  self.source)
