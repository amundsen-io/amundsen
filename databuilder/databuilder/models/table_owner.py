# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    List, Optional, Union,
)

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.owner_constants import OWNER_OF_OBJECT_RELATION_TYPE, OWNER_RELATION_TYPE
from databuilder.models.user import User


class TableOwner(GraphSerializable):
    """
    Hive table owner model.
    """
    OWNER_TABLE_RELATION_TYPE = OWNER_OF_OBJECT_RELATION_TYPE
    TABLE_OWNER_RELATION_TYPE = OWNER_RELATION_TYPE

    def __init__(self,
                 db_name: str,
                 schema: str,
                 table_name: str,
                 owners: Union[List, str],
                 cluster: str = 'gold',
                 ) -> None:
        self.db = db_name
        self.schema = schema
        self.table = table_name
        if isinstance(owners, str):
            owners = owners.split(',')
        self.owners = [owner.strip() for owner in owners]

        self.cluster = cluster
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

    def get_owner_model_key(self, owner: str) -> str:
        return User.USER_NODE_KEY_FORMAT.format(email=owner)

    def get_metadata_model_key(self) -> str:
        return f'{self.db}://{self.cluster}.{self.schema}/{self.table}'

    def create_nodes(self) -> List[GraphNode]:
        """
        Create a list of Neo4j node records
        :return:
        """
        results = []
        for owner in self.owners:
            if owner:
                node = GraphNode(
                    key=self.get_owner_model_key(owner),
                    label=User.USER_NODE_LABEL,
                    attributes={
                        User.USER_NODE_EMAIL: owner
                    }
                )
                results.append(node)
        return results

    def create_relation(self) -> List[GraphRelationship]:
        """
        Create a list of relation map between owner record with original hive table
        :return:
        """
        results = []
        for owner in self.owners:
            relationship = GraphRelationship(
                start_key=self.get_owner_model_key(owner),
                start_label=User.USER_NODE_LABEL,
                end_key=self.get_metadata_model_key(),
                end_label='Table',
                type=TableOwner.OWNER_TABLE_RELATION_TYPE,
                reverse_type=TableOwner.TABLE_OWNER_RELATION_TYPE,
                attributes={}
            )
            results.append(relationship)

        return results

    def __repr__(self) -> str:
        return f'TableOwner({self.db!r}, {self.cluster!r}, {self.schema!r}, {self.table!r}, {self.owners!r})'
