# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, Union

from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable, NODE_KEY, NODE_LABEL


class Neo4jESLastUpdated(Neo4jCsvSerializable):
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

    def create_next_node(self) -> Union[Dict[str, Any], None]:
        """
        Will create an orphan node for last updated timestamp.
        :return:
        """
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_nodes(self) -> List[Dict[str, Any]]:
        """
        Create a list of Neo4j node records.
        :return:
        """
        return [{
            NODE_KEY: Neo4jESLastUpdated.KEY,
            NODE_LABEL: Neo4jESLastUpdated.LABEL,
            Neo4jESLastUpdated.LATEST_TIMESTAMP: self.timestamp
        }]

    def create_next_relation(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._rel_iter)
        except StopIteration:
            return None

    def create_relation(self) -> List[Dict[str, Any]]:
        return []
