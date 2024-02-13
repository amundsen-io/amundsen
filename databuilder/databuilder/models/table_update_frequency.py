from typing import (
    Iterator, Optional, Union,
)
from enum import Enum
import logging

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import TableMetadata


LOGGER = logging.getLogger(__name__)


class UpdateFrequency(Enum):
    ANNUALLY = "annually"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"

    def get_enum_by_value(value):
        for member in UpdateFrequency:
            if member.value == value:
                return member
        return None


class TableUpdateFrequency(GraphSerializable):
    LABEL = 'Update_Frequency'
    NODE_KEY_FORMAT = '{table_key}/updatefrequency'
    UPDATE_FREQUENCY_TABLE_RELATION_TYPE = 'UPDATE_FREQUENCY_OF'
    TABLE_UPDATE_FREQUENCY_RELATION_TYPE = 'UPDATE_FREQUENCY'

    def __init__(self,
                 db_name: str,
                 schema: str,
                 table_name: str,
                 cluster: str,
                 frequency: str,
                 ) -> None:
        self.db = db_name
        self.schema = schema
        self.table = table_name
        self.cluster = cluster

        self.frequency: UpdateFrequency = UpdateFrequency.get_enum_by_value(frequency.lower())
        if not self.frequency:
            LOGGER.warning("No Update Frequency provide, node will not be created")
            self._node_iter = None
            self._relation_iter = None
        else:
            self._node_iter = self._create_node_iterator()
            self._relation_iter = self._create_relation_iterator()

    def create_next_node(self) -> Optional[GraphNode]:
        # return the string representation of the data
        try:
            if self._node_iter:
                return next(self._node_iter)
            else:
                None
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        try:
            if self._relation_iter:
                return next(self._relation_iter)
            else:
                return None
        except StopIteration:
            return None

    def get_source_model_key(self) -> str:
        return NODE_KEY_FORMAT.format(table_key=self.get_table_model_key)

    def get_table_model_key(self) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.db,
                                                    cluster=self.cluster,
                                                    schema=self.schema,
                                                    tbl=self.table)

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        """
        Create a table source node
        :return:
        """
        node = GraphNode(
            key=self.get_source_model_key(),
            label=self.LABEL,
            attributes={
                'frequency': self.frequency.value
            }
        )
        yield node

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        """
        Create relation map between owner record with original hive table
        :return:
        """
        relationship = GraphRelationship(
            start_label=self.LABEL,
            start_key=self.get_source_model_key(),
            end_label=TableMetadata.TABLE_NODE_LABEL,
            end_key=self.get_table_model_key(),
            type=self.UPDATE_FREQUENCY_TABLE_RELATION_TYPE,
            reverse_type=self.TABLE_UPDATE_FREQUENCY_RELATION_TYPE,
            attributes={}
        )
        yield relationship

    def __repr__(self) -> str:
        return f'TableUpdateFrequency({self.db!r}, {self.cluster!r}, {self.schema!r}, {self.table!r}, {self.frequency!r})'
