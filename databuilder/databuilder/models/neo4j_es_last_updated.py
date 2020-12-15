# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Union

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable


class Neo4jESLastUpdated(GraphSerializable):
    """
    Data model to keep track the last updated timestamp for
    neo4j and es.
    """

    LABEL = 'Updatedtimestamp'
    KEY = 'amundsen_updated_timestamp'
    LATEST_TIMESTAMP = 'latest_timestmap'

    def __init__(self,
                 timestamp: int,
                 ) -> None:
        """
        :param timestamp: epoch for latest updated timestamp for neo4j an es
        """
        self.timestamp = timestamp
        self._node_iter = iter(self.create_nodes())
        self._rel_iter = iter(self.create_relation())

    def create_next_node(self) -> Union[GraphNode, None]:
        """
        Will create an orphan node for last updated timestamp.
        """
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_nodes(self) -> List[GraphNode]:
        """
        Create a list of Neo4j node records.
        """
        node = GraphNode(
            key=Neo4jESLastUpdated.KEY,
            label=Neo4jESLastUpdated.LABEL,
            attributes={
                Neo4jESLastUpdated.LATEST_TIMESTAMP: self.timestamp
            }
        )
        return [node]

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._rel_iter)
        except StopIteration:
            return None

    def create_relation(self) -> List[GraphRelationship]:
        return []
