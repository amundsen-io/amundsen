# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Any, Iterator, Optional, Union,
)

from databuilder.models.atlas_entity import AtlasEntity
from databuilder.models.atlas_relationship import AtlasRelationship
from databuilder.models.atlas_serializable import AtlasSerializable
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable

DESCRIPTION_NODE_LABEL_VAL = 'Description'
DESCRIPTION_NODE_LABEL = DESCRIPTION_NODE_LABEL_VAL


class DescriptionMetadata(GraphSerializable, AtlasSerializable):
    DESCRIPTION_NODE_LABEL = DESCRIPTION_NODE_LABEL_VAL
    PROGRAMMATIC_DESCRIPTION_NODE_LABEL = 'Programmatic_Description'
    DESCRIPTION_KEY_FORMAT = '{description}'
    DESCRIPTION_TEXT = 'description'
    DESCRIPTION_SOURCE = 'description_source'

    DESCRIPTION_RELATION_TYPE = 'DESCRIPTION'
    INVERSE_DESCRIPTION_RELATION_TYPE = 'DESCRIPTION_OF'

    # The default editable source.
    DEFAULT_SOURCE = "description"

    def __init__(self,
                 text: Optional[str],
                 source: str = DEFAULT_SOURCE,
                 description_key: Optional[str] = None,
                 start_label: Optional[str] = None,  # Table, Column, Schema, Type_Metadata
                 start_key: Optional[str] = None,
                 ):
        """
        :param source: The unique source of what is populating this description.
        :param text: the description text. Markdown supported.
        """
        self.source = source
        self.text = text
        #  There are so many dependencies on Description node, that it is probably easier to just separate the rest out.
        if self.source == self.DEFAULT_SOURCE:
            self.label = self.DESCRIPTION_NODE_LABEL
        else:
            self.label = self.PROGRAMMATIC_DESCRIPTION_NODE_LABEL

        self.start_label = start_label
        self.start_key = start_key
        self.description_key = description_key or self.get_description_default_key(start_key)

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DescriptionMetadata):
            return (self.text == other.text and
                    self.source == other.source and
                    self.description_key == other.description_key and
                    self.start_label == other.start_label and
                    self.start_key == self.start_key)
        return False

    @staticmethod
    def create_description_metadata(text: Union[None, str],
                                    source: Optional[str] = DEFAULT_SOURCE,
                                    description_key: Optional[str] = None,
                                    start_label: Optional[str] = None,  # Table, Column, Schema
                                    start_key: Optional[str] = None,
                                    ) -> Optional['DescriptionMetadata']:
        # We do not want to create a node if there is no description text!
        if text is None:
            return None
        description_node = DescriptionMetadata(text=text,
                                               source=source or DescriptionMetadata.DEFAULT_SOURCE,
                                               description_key=description_key,
                                               start_label=start_label,
                                               start_key=start_key)
        return description_node

    def get_description_id(self) -> str:
        if self.source == self.DEFAULT_SOURCE:
            return "_description"
        else:
            return "_" + self.source + "_description"

    def get_description_default_key(self, start_key: Optional[str]) -> Optional[str]:
        return f'{start_key}/{self.get_description_id()}' if start_key else None

    def get_node(self, node_key: str) -> GraphNode:
        node = GraphNode(
            key=node_key,
            label=self.label,
            attributes={
                DescriptionMetadata.DESCRIPTION_SOURCE: self.source,
                DescriptionMetadata.DESCRIPTION_TEXT: self.text
            }
        )
        return node

    def get_relation(self,
                     start_node: str,
                     start_key: str,
                     end_key: str,
                     ) -> GraphRelationship:
        relationship = GraphRelationship(
            start_label=start_node,
            start_key=start_key,
            end_label=self.label,
            end_key=end_key,
            type=DescriptionMetadata.DESCRIPTION_RELATION_TYPE,
            reverse_type=DescriptionMetadata.INVERSE_DESCRIPTION_RELATION_TYPE,
            attributes={}
        )
        return relationship

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

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.description_key:
            raise Exception('Required description node key cannot be None')
        yield self.get_node(self.description_key)

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.start_label:
            raise Exception('Required relation start node label cannot be None')
        if not self.start_key:
            raise Exception('Required relation start key cannot be None')
        if not self.description_key:
            raise Exception('Required relation end key cannot be None')
        yield self.get_relation(
            start_node=self.start_label,
            start_key=self.start_key,
            end_key=self.description_key
        )

    def create_next_atlas_relation(self) -> Union[AtlasRelationship, None]:
        pass

    def create_next_atlas_entity(self) -> Union[AtlasEntity, None]:
        pass

    def __repr__(self) -> str:
        return f'DescriptionMetadata({self.source!r}, {self.text!r})'
