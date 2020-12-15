# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import TableMetadata


class TableSource(GraphSerializable):
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
                 source_type: str = 'github',
                 ) -> None:
        self.db = db_name
        self.schema = schema
        self.table = table_name

        self.cluster = cluster if cluster else 'gold'
        # source is the source file location
        self.source = source
        self.source_type = source_type
        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def create_next_node(self) -> Optional[GraphNode]:
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
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
        return f'{self.db}://{self.cluster}.{self.schema}/{self.table}'

    def create_nodes(self) -> List[GraphNode]:
        """
        Create a list of Neo4j node records
        :return:
        """
        node = GraphNode(
            key=self.get_source_model_key(),
            label=TableSource.LABEL,
            attributes={
                'source': self.source,
                'source_type': self.source_type
            }
        )
        results = [node]
        return results

    def create_relation(self) -> List[GraphRelationship]:
        """
        Create a list of relation map between owner record with original hive table
        :return:
        """
        relationship = GraphRelationship(
            start_label=TableSource.LABEL,
            start_key=self.get_source_model_key(),
            end_label=TableMetadata.TABLE_NODE_LABEL,
            end_key=self.get_metadata_model_key(),
            type=TableSource.SOURCE_TABLE_RELATION_TYPE,
            reverse_type=TableSource.TABLE_SOURCE_RELATION_TYPE,
            attributes={}
        )
        results = [relationship]
        return results

    def __repr__(self) -> str:
        return f'TableSource({self.db!r}, {self.cluster!r}, {self.schema!r}, {self.table!r}, {self.source!r})'
