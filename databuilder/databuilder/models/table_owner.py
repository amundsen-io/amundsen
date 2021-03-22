# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Iterator, List, Optional, Union,
)

from amundsen_rds.models import RDSModel
from amundsen_rds.models.table import TableOwner as RDSTableOwner
from amundsen_rds.models.user import User as RDSUser

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.owner_constants import OWNER_OF_OBJECT_RELATION_TYPE, OWNER_RELATION_TYPE
from databuilder.models.table_serializable import TableSerializable
from databuilder.models.user import User


class TableOwner(GraphSerializable, TableSerializable):
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
        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()
        self._record_iter = self._create_record_iterator()

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

    def create_next_record(self) -> Union[RDSModel, None]:
        try:
            return next(self._record_iter)
        except StopIteration:
            return None

    def get_owner_model_key(self, owner: str) -> str:
        return User.USER_NODE_KEY_FORMAT.format(email=owner)

    def get_metadata_model_key(self) -> str:
        return f'{self.db}://{self.cluster}.{self.schema}/{self.table}'

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        """
        Create table owner nodes
        :return:
        """
        for owner in self.owners:
            if owner:
                node = GraphNode(
                    key=self.get_owner_model_key(owner),
                    label=User.USER_NODE_LABEL,
                    attributes={
                        User.USER_NODE_EMAIL: owner
                    }
                )
                yield node

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        """
        Create relation map between owner record with original hive table
        :return:
        """
        for owner in self.owners:
            if owner:
                relationship = GraphRelationship(
                    start_key=self.get_owner_model_key(owner),
                    start_label=User.USER_NODE_LABEL,
                    end_key=self.get_metadata_model_key(),
                    end_label='Table',
                    type=TableOwner.OWNER_TABLE_RELATION_TYPE,
                    reverse_type=TableOwner.TABLE_OWNER_RELATION_TYPE,
                    attributes={}
                )
                yield relationship

    def _create_record_iterator(self) -> Iterator[RDSModel]:
        for owner in self.owners:
            if owner:
                user_record = RDSUser(
                    rk=self.get_owner_model_key(owner),
                    email=owner
                )
                yield user_record

                table_owner_record = RDSTableOwner(
                    table_rk=self.get_metadata_model_key(),
                    user_rk=self.get_owner_model_key(owner)
                )
                yield table_owner_record

    def __repr__(self) -> str:
        return f'TableOwner({self.db!r}, {self.cluster!r}, {self.schema!r}, {self.table!r}, {self.owners!r})'
