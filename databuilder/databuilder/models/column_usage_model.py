# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Iterator, Union

from amundsen_rds.models import RDSModel
from amundsen_rds.models.table import TableUsage as RDSTableUsage

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.table_serializable import TableSerializable
from databuilder.models.usage.usage_constants import (
    READ_RELATION_COUNT_PROPERTY, READ_RELATION_TYPE, READ_REVERSE_RELATION_TYPE,
)
from databuilder.models.user import User


class ColumnUsageModel(GraphSerializable, TableSerializable):
    """
    A model represents user <--> column graph model
    Currently it only support to serialize to table level
    """
    TABLE_NODE_LABEL = TableMetadata.TABLE_NODE_LABEL
    TABLE_NODE_KEY_FORMAT = TableMetadata.TABLE_KEY_FORMAT

    USER_TABLE_RELATION_TYPE = READ_RELATION_TYPE
    TABLE_USER_RELATION_TYPE = READ_REVERSE_RELATION_TYPE

    # Property key for relationship read, readby relationship
    READ_RELATION_COUNT = READ_RELATION_COUNT_PROPERTY

    def __init__(self,
                 database: str,
                 cluster: str,
                 schema: str,
                 table_name: str,
                 column_name: str,
                 user_email: str,
                 read_count: int,
                 ) -> None:
        self.database = database
        self.cluster = cluster
        self.schema = schema
        self.table_name = table_name
        self.column_name = column_name
        self.user_email = user_email
        self.read_count = int(read_count)

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()
        self._record_iter = self._create_record_iterator()

    def create_next_node(self) -> Union[GraphNode, None]:

        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        """
        Create an user node
        :return:
        """
        user_node = User(email=self.user_email).get_user_node()
        yield user_node

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        relationship = GraphRelationship(
            start_key=self._get_table_key(),
            start_label=TableMetadata.TABLE_NODE_LABEL,
            end_key=self._get_user_key(self.user_email),
            end_label=User.USER_NODE_LABEL,
            type=ColumnUsageModel.TABLE_USER_RELATION_TYPE,
            reverse_type=ColumnUsageModel.USER_TABLE_RELATION_TYPE,
            attributes={
                ColumnUsageModel.READ_RELATION_COUNT: self.read_count
            }
        )
        yield relationship

    def create_next_record(self) -> Union[RDSModel, None]:
        try:
            return next(self._record_iter)
        except StopIteration:
            return None

    def _create_record_iterator(self) -> Iterator[RDSModel]:
        user_record = User(email=self.user_email).get_user_record()
        yield user_record

        table_usage_record = RDSTableUsage(
            user_rk=self._get_user_key(self.user_email),
            table_rk=self._get_table_key(),
            read_count=self.read_count
        )
        yield table_usage_record

    def _get_table_key(self) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.database,
                                                     cluster=self.cluster,
                                                     schema=self.schema,
                                                     tbl=self.table_name)

    def _get_user_key(self, email: str) -> str:
        return User.get_user_model_key(email=email)

    def __repr__(self) -> str:
        return f'TableColumnUsage({self.database!r}, {self.cluster!r}, {self.schema!r}, ' \
               f'{self.table_name!r}, {self.column_name!r}, {self.user_email!r}, {self.read_count!r})'
