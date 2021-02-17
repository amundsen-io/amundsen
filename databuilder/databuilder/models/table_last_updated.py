# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Union

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.timestamp import timestamp_constants


class TableLastUpdated(GraphSerializable):
    # constants
    LAST_UPDATED_NODE_LABEL = timestamp_constants.NODE_LABEL
    LAST_UPDATED_KEY_FORMAT = '{db}://{cluster}.{schema}/{tbl}/timestamp'
    TIMESTAMP_PROPERTY = timestamp_constants.DEPRECATED_TIMESTAMP_PROPERTY
    TIMESTAMP_NAME_PROPERTY = timestamp_constants.TIMESTAMP_NAME_PROPERTY

    TABLE_LASTUPDATED_RELATION_TYPE = timestamp_constants.LASTUPDATED_RELATION_TYPE
    LASTUPDATED_TABLE_RELATION_TYPE = timestamp_constants.LASTUPDATED_REVERSE_RELATION_TYPE

    def __init__(self,
                 table_name: str,
                 last_updated_time_epoch: int,
                 schema: str,
                 db: str = 'hive',
                 cluster: str = 'gold'
                 ) -> None:
        self.table_name = table_name
        self.last_updated_time = int(last_updated_time_epoch)
        self.schema = schema
        self.db = db
        self.cluster = cluster

        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def __repr__(self) -> str:
        return f"TableLastUpdated(table_name={self.table_name!r}, last_updated_time={self.last_updated_time!r}, " \
               f"schema={self.schema!r}, db={self.db!r}, cluster={self.cluster!r})"

    def create_next_node(self) -> Union[GraphNode, None]:
        # creates new node
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def get_table_model_key(self) -> str:
        # returns formatted string for table name
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.db,
                                                     cluster=self.cluster,
                                                     schema=self.schema,
                                                     tbl=self.table_name)

    def get_last_updated_model_key(self) -> str:
        # returns formatted string for last updated name
        return TableLastUpdated.LAST_UPDATED_KEY_FORMAT.format(db=self.db,
                                                               cluster=self.cluster,
                                                               schema=self.schema,
                                                               tbl=self.table_name)

    def create_nodes(self) -> List[GraphNode]:
        """
        Create a list of graph node records
        :return:
        """
        results = []

        node = GraphNode(
            key=self.get_last_updated_model_key(),
            label=TableLastUpdated.LAST_UPDATED_NODE_LABEL,
            attributes={
                TableLastUpdated.TIMESTAMP_PROPERTY: self.last_updated_time,
                timestamp_constants.TIMESTAMP_PROPERTY: self.last_updated_time,
                TableLastUpdated.TIMESTAMP_NAME_PROPERTY: timestamp_constants.TimestampName.last_updated_timestamp.name
            }
        )

        results.append(node)

        return results

    def create_relation(self) -> List[GraphRelationship]:
        """
        Create a list of relations mapping last updated node with table node
        :return:
        """
        relationship = GraphRelationship(
            start_label=TableMetadata.TABLE_NODE_LABEL,
            start_key=self.get_table_model_key(),
            end_label=TableLastUpdated.LAST_UPDATED_NODE_LABEL,
            end_key=self.get_last_updated_model_key(),
            type=TableLastUpdated.TABLE_LASTUPDATED_RELATION_TYPE,
            reverse_type=TableLastUpdated.LASTUPDATED_TABLE_RELATION_TYPE,
            attributes={}
        )
        results = [relationship]

        return results
