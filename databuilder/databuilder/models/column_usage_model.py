# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Union, Dict, Any, Iterable, List

from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, RELATION_START_KEY, RELATION_END_KEY,
    RELATION_START_LABEL, RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE
)
from databuilder.models.usage.usage_constants import (
    READ_RELATION_TYPE, READ_REVERSE_RELATION_TYPE, READ_RELATION_COUNT_PROPERTY
)
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.user import User


class ColumnUsageModel(Neo4jCsvSerializable):

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
        self.read_count = read_count

        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def create_next_node(self) -> Union[Dict[str, Any], None]:

        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_nodes(self) -> List[Dict[str, Any]]:
        """
        Create a list of Neo4j node records
        :return:
        """

        return User(email=self.user_email).create_nodes()

    def create_next_relation(self) -> Union[Dict[str, Any], None]:

        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def create_relation(self) -> Iterable[Any]:
        return [{
            RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
            RELATION_END_LABEL: User.USER_NODE_LABEL,
            RELATION_START_KEY: self._get_table_key(),
            RELATION_END_KEY: self._get_user_key(self.user_email),
            RELATION_TYPE: ColumnUsageModel.TABLE_USER_RELATION_TYPE,
            RELATION_REVERSE_TYPE: ColumnUsageModel.USER_TABLE_RELATION_TYPE,
            ColumnUsageModel.READ_RELATION_COUNT: self.read_count
        }]

    def _get_table_key(self) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.database,
                                                     cluster=self.cluster,
                                                     schema=self.schema,
                                                     tbl=self.table_name)

    def _get_user_key(self, email: str) -> str:
        return User.get_user_model_key(email=email)

    def __repr__(self) -> str:
        return 'TableColumnUsage({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r})'.format(self.database,
                                                                                   self.cluster,
                                                                                   self.schema,
                                                                                   self.table_name,
                                                                                   self.column_name,
                                                                                   self.user_email,
                                                                                   self.read_count)
