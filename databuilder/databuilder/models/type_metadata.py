# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import Iterable, Iterator, Optional, Union

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import DescriptionMetadata


class TypeMetadata(abc.ABC, GraphSerializable):
    TYPE_NODE_LABEL = 'Column_Subtype'
    TYPE_RELATION_TYPE = 'COLUMN_SUBTYPE'
    INVERSE_TYPE_RELATION_TYPE = 'COLUMN_SUBTYPE_OF'
    TYPE_KIND = 'kind'
    TYPE_NAME = 'name'
    TYPE_DESCRIPTION = 'description'
    TYPE_DATA_TYPE = 'data_type'
    TYPE_MAP_KEY = 'map_key'
    TYPE_MAP_VALUE = 'map_value'
    TYPE_SORT_ORDER = 'sort_order'

    @abc.abstractmethod
    def __init__(self,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        self.start_label = start_label
        self.start_key = start_key

        self._node_iter = self.create_node_iterator()
        self._relation_iter = self.create_relation_iterator()

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def is_terminal_type(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def create_node_iterator(self) -> Iterator[GraphNode]:
        raise NotImplementedError

    @abc.abstractmethod
    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        raise NotImplementedError

    def create_next_node(self) -> Optional[GraphNode]:
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None


class ArrayTypeMetadata(TypeMetadata):
    def __init__(self,
                 data_type: Union[TypeMetadata, str],
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(ArrayTypeMetadata, self).__init__(start_label, start_key)
        self.data_type = data_type

    def __eq__(self, other) -> bool:
        if isinstance(other, ArrayTypeMetadata):
            return (self.data_type.__eq__(other.data_type)
                    and self.start_label == other.start_label
                    and self.start_key == other.start_key)
        return False

    def __str__(self) -> str:
        return f"array<{self.data_type.__str__()}>"

    def is_terminal_type(self) -> bool:
        return not isinstance(self.data_type, TypeMetadata)

    def _get_node_key(self, start_key: str) -> str:
        return f"{start_key}/array"

    def _get_node(self, start_key: str) -> GraphNode:
        node = GraphNode(
            key=self._get_node_key(start_key),
            label=TypeMetadata.TYPE_NODE_LABEL,
            attributes={
                TypeMetadata.TYPE_KIND: 'array',
                TypeMetadata.TYPE_DATA_TYPE: self.data_type.__str__()
            }
        )
        return node

    def _get_relation(self,
                      start_label: str,
                      start_key: str) -> GraphRelationship:
        relation = GraphRelationship(
            start_label=start_label,
            start_key=start_key,
            end_label=TypeMetadata.TYPE_NODE_LABEL,
            end_key=self._get_node_key(start_key),
            type=TypeMetadata.TYPE_RELATION_TYPE,
            reverse_type=TypeMetadata.INVERSE_TYPE_RELATION_TYPE,
            attributes={}
        )
        return relation

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if not self.is_terminal_type():
            yield self._get_node(self.start_key)
            yield from self.data_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.start_label:
            raise Exception('Required start node label cannot be None')
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if not self.is_terminal_type():
            yield self._get_relation(self.start_label, self.start_key)
            yield from self.data_type.create_relation_iterator()


class MapTypeMetadata(TypeMetadata):
    def __init__(self,
                 key: str,
                 value: Union[TypeMetadata, str],
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(MapTypeMetadata, self).__init__(start_label, start_key)
        self.key = key
        self.value = value

    def __eq__(self, other) -> bool:
        if isinstance(other, MapTypeMetadata):
            return (self.key == other.key
                    and self.value.__eq__(other.value)
                    and self.start_label == other.start_label
                    and self.start_key == other.start_key)
        return False

    def __str__(self) -> str:
        return f"map<{self.key},{self.value.__str__()}>"

    def is_terminal_type(self) -> bool:
        return not isinstance(self.value, TypeMetadata)

    def _get_node_key(self, start_key: str) -> str:
        return f"{start_key}/map"

    def _get_node(self, start_key: str) -> GraphNode:
        node = GraphNode(
            key=self._get_node_key(start_key),
            label=TypeMetadata.TYPE_NODE_LABEL,
            attributes={
                TypeMetadata.TYPE_KIND: 'map',
                TypeMetadata.TYPE_MAP_KEY: self.key.__str__(),
                TypeMetadata.TYPE_MAP_VALUE: self.value.__str__()
            }
        )
        return node

    def _get_relation(self,
                      start_label: str,
                      start_key: str) -> GraphRelationship:
        relation = GraphRelationship(
            start_label=start_label,
            start_key=start_key,
            end_label=TypeMetadata.TYPE_NODE_LABEL,
            end_key=self._get_node_key(start_key),
            type=TypeMetadata.TYPE_RELATION_TYPE,
            reverse_type=TypeMetadata.INVERSE_TYPE_RELATION_TYPE,
            attributes={}
        )
        return relation

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if not self.is_terminal_type():
            yield self._get_node(self.start_key)
            yield from self.value.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.start_label:
            raise Exception('Required start node label cannot be None')
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if not self.is_terminal_type():
            yield self._get_relation(self.start_label, self.start_key)
            yield from self.value.create_relation_iterator()


class StructItem():
    def __init__(self,
                 name: str,
                 description: Union[str, None],
                 data_type: Union[TypeMetadata, str]) -> None:
        self.name = name
        self.description = DescriptionMetadata.create_description_metadata(
            source=None,
            text=description
        )
        self.data_type = data_type

    def __eq__(self, other) -> bool:
        if isinstance(other, StructItem):
            return (self.name == other.name
                    and self.data_type.__eq__(other.data_type))
        return False


class StructTypeMetadata(TypeMetadata):
    def __init__(self,
                 struct_items: Iterable[StructItem],
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(StructTypeMetadata, self).__init__(start_label, start_key)
        self.struct_items = struct_items

    def __eq__(self, other) -> bool:
        if isinstance(other, StructTypeMetadata):
            for item in self.struct_items:
                if item not in other.struct_items:
                    return False
            return (self.start_label == other.start_label
                    and self.start_key == other.start_key)
        return False

    def __str__(self) -> str:
        inner_string = ''
        for item in self.struct_items:
            inner_string += f"{item.name}:{item.data_type.__str__()},"
        return f"struct<{inner_string[:-1]}>"

    def is_terminal_type(self) -> bool:
        return False

    def _get_node_key(self, start_key: str, name: str) -> str:
        return f"{start_key}/{name}"

    def _get_description_key(self,
                             start_key: str,
                             name: str,
                             description: DescriptionMetadata) -> str:
        node_key = self._get_node_key(start_key, name)
        description_id = description.get_description_id()
        return f"{node_key}/{description_id}"

    def _get_node(self,
                  start_key: str,
                  name: str,
                  data_type: Union[TypeMetadata, str],
                  sort_order: int) -> GraphNode:
        node = GraphNode(
            key=self._get_node_key(start_key, name),
            label=TypeMetadata.TYPE_NODE_LABEL,
            attributes={
                TypeMetadata.TYPE_KIND: 'struct',
                TypeMetadata.TYPE_NAME: name,
                TypeMetadata.TYPE_DATA_TYPE: data_type.__str__(),
                TypeMetadata.TYPE_SORT_ORDER: sort_order
            }
        )
        return node

    def _get_relation(self,
                      start_label: str,
                      start_key: str,
                      name: str) -> GraphRelationship:
        relation = GraphRelationship(
            start_label=start_label,
            start_key=start_key,
            end_label=TypeMetadata.TYPE_NODE_LABEL,
            end_key=self._get_node_key(start_key, name),
            type=TypeMetadata.TYPE_RELATION_TYPE,
            reverse_type=TypeMetadata.INVERSE_TYPE_RELATION_TYPE,
            attributes={}
        )
        return relation

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        sort_order = 0
        for item in self.struct_items:
            yield self._get_node(self.start_key,
                                 item.name,
                                 item.data_type,
                                 sort_order)
            sort_order += 1

            if item.description:
                descr_key = self._get_description_key(self.start_key,
                                                      item.name,
                                                      item.description)
                yield item.description.get_node(descr_key)

            if isinstance(item.data_type, TypeMetadata):
                yield from item.data_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.start_label:
            raise Exception('Required start node label cannot be None')
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        for item in self.struct_items:
            yield self._get_relation(self.start_label,
                                     self.start_key,
                                     item.name)

            if item.description:
                node_key = self._get_node_key(self.start_key, item.name)
                descr_key = self._get_description_key(self.start_key,
                                                      item.name,
                                                      item.description)
                yield item.description.get_relation(
                    TypeMetadata.TYPE_NODE_LABEL,
                    node_key,
                    descr_key
                )

            if isinstance(item.data_type, TypeMetadata):
                yield from item.data_type.create_relation_iterator()
