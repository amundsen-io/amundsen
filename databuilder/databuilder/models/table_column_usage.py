# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Iterable, Iterator, Union,
)

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.user import User


class ColumnReader(object):
    """
    A class represent user's read action on column. Implicitly assumes that read count is one.
    """

    def __init__(self,
                 database: str,
                 cluster: str,
                 schema: str,
                 table: str,
                 column: str,
                 user_email: str,
                 read_count: int = 1
                 ) -> None:
        self.database = database
        self.cluster = cluster
        self.schema = schema
        self.table = table
        self.column = column
        self.user_email = user_email
        self.read_count = int(read_count)

    def __repr__(self) -> str:
        return f"ColumnReader(database={self.database!r}, cluster={self.cluster!r}, " \
               f"schema={self.schema!r}, table={self.table!r}, column={self.column!r}, " \
               f"user_email={self.user_email!r}, read_count={self.read_count!r})"


class TableColumnUsage(GraphSerializable):
    """
    A model represents user <--> column graph model
    Currently it only support to serialize to table level
    """
    TABLE_NODE_LABEL = TableMetadata.TABLE_NODE_LABEL
    TABLE_NODE_KEY_FORMAT = TableMetadata.TABLE_KEY_FORMAT

    USER_TABLE_RELATION_TYPE = 'READ'
    TABLE_USER_RELATION_TYPE = 'READ_BY'

    # Property key for relationship read, readby relationship
    READ_RELATION_COUNT = 'read_count'

    def __init__(self, col_readers: Iterable[ColumnReader]) -> None:
        for col_reader in col_readers:
            if col_reader.column != '*':
                raise NotImplementedError(f'Column is not supported yet {col_readers}')

        self.col_readers = col_readers
        self._node_iterator = self._create_node_iterator()
        self._rel_iter = self._create_rel_iterator()

    def create_next_node(self) -> Union[GraphNode, None]:
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        for col_reader in self.col_readers:
            if col_reader.column == '*':
                # using yield for better memory efficiency
                yield User(email=col_reader.user_email).create_nodes()[0]

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._rel_iter)
        except StopIteration:
            return None

    def _create_rel_iterator(self) -> Iterator[GraphRelationship]:
        for col_reader in self.col_readers:
            relationship = GraphRelationship(
                start_label=TableMetadata.TABLE_NODE_LABEL,
                start_key=self._get_table_key(col_reader),
                end_label=User.USER_NODE_LABEL,
                end_key=self._get_user_key(col_reader.user_email),
                type=TableColumnUsage.TABLE_USER_RELATION_TYPE,
                reverse_type=TableColumnUsage.USER_TABLE_RELATION_TYPE,
                attributes={
                    TableColumnUsage.READ_RELATION_COUNT: col_reader.read_count
                }
            )
            yield relationship

    def _get_table_key(self, col_reader: ColumnReader) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=col_reader.database,
                                                     cluster=col_reader.cluster,
                                                     schema=col_reader.schema,
                                                     tbl=col_reader.table)

    def _get_user_key(self, email: str) -> str:
        return User.get_user_model_key(email=email)

    def __repr__(self) -> str:
        return f'TableColumnUsage(col_readers={self.col_readers!r})'
