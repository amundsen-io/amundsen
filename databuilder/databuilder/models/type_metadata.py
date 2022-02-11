# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import (
    Any, Dict, Iterator, Optional,
)

from databuilder.models.description_metadata import DescriptionMetadata
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable


class TypeMetadata(abc.ABC, GraphSerializable):
    NODE_LABEL = 'Subtype'
    RELATION_TYPE = 'SUBTYPE'
    INVERSE_RELATION_TYPE = 'SUBTYPE_OF'
    KIND = 'kind'
    NAME = 'name'
    DESCRIPTION = 'description'
    DATA_TYPE = 'data_type'
    MAP_KEY = 'map_key'
    MAP_VALUE = 'map_value'
    SORT_ORDER = 'sort_order'

    @abc.abstractmethod
    def __init__(self,
                 type_str: str,
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        self.type_str = type_str
        self.description = DescriptionMetadata.create_description_metadata(
            source=None,
            text=description
        )
        self.start_label = start_label
        self.start_key = start_key

        self._node_iter = self.create_node_iterator()
        self._relation_iter = self.create_relation_iterator()

    @abc.abstractmethod
    def __eq__(self, other: Any) -> bool:
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

    def __str__(self) -> str:
        return self.type_str

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

    def get_node_key(self, name: str) -> str:
        return f"{self.start_key}/{name}"

    def get_description_key(self) -> str:
        if self.start_key and self.description:
            description_id = self.description.get_description_id()
            return f"{self.start_key}/{description_id}"
        return ''


class ArrayTypeMetadata(TypeMetadata):
    def __init__(self,
                 data_type: TypeMetadata,
                 type_str: str,
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(ArrayTypeMetadata, self).__init__(type_str, description, start_label, start_key)
        self.data_type = data_type

        self.name = '__array_inner'
        self.kind = 'array'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ArrayTypeMetadata):
            return (self.data_type == other.data_type and
                    self.type_str == other.type_str and
                    self.start_label == other.start_label and
                    self.start_key == other.start_key)
        return False

    def is_terminal_type(self) -> bool:
        return isinstance(self.data_type, ScalarTypeMetadata)

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if self.description:
            yield self.description.get_node(self.get_description_key())

        if not self.is_terminal_type():
            yield GraphNode(
                key=self.get_node_key(self.name),
                label=TypeMetadata.NODE_LABEL,
                attributes={
                    TypeMetadata.KIND: self.kind,
                    TypeMetadata.DATA_TYPE: self.data_type.__str__()
                }
            )
            yield from self.data_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.start_label:
            raise Exception('Required start node label cannot be None')
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if self.description:
            yield self.description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.start_key,
                self.get_description_key()
            )

        if not self.is_terminal_type():
            yield GraphRelationship(
                start_label=self.start_label,
                start_key=self.start_key,
                end_label=TypeMetadata.NODE_LABEL,
                end_key=self.get_node_key(self.name),
                type=TypeMetadata.RELATION_TYPE,
                reverse_type=TypeMetadata.INVERSE_RELATION_TYPE,
                attributes={}
            )
            yield from self.data_type.create_relation_iterator()


class MapTypeMetadata(TypeMetadata):
    def __init__(self,
                 key: str,
                 value: TypeMetadata,
                 type_str: str,
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(MapTypeMetadata, self).__init__(type_str, description, start_label, start_key)
        self.key = key
        self.value = value

        self.name = '__map_inner'
        self.kind = 'map'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MapTypeMetadata):
            return (self.key == other.key and
                    self.value == other.value and
                    self.type_str == other.type_str and
                    self.start_label == other.start_label and
                    self.start_key == other.start_key)
        return False

    def is_terminal_type(self) -> bool:
        return isinstance(self.value, ScalarTypeMetadata)

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if self.description:
            yield self.description.get_node(self.get_description_key())

        if not self.is_terminal_type():
            yield GraphNode(
                key=self.get_node_key(self.name),
                label=TypeMetadata.NODE_LABEL,
                attributes={
                    TypeMetadata.KIND: self.kind,
                    TypeMetadata.MAP_KEY: self.key,
                    TypeMetadata.MAP_VALUE: self.value.__str__()
                }
            )
            yield from self.value.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.start_label:
            raise Exception('Required start node label cannot be None')
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if self.description:
            yield self.description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.start_key,
                self.get_description_key()
            )

        if not self.is_terminal_type():
            yield GraphRelationship(
                start_label=self.start_label,
                start_key=self.start_key,
                end_label=TypeMetadata.NODE_LABEL,
                end_key=self.get_node_key(self.name),
                type=TypeMetadata.RELATION_TYPE,
                reverse_type=TypeMetadata.INVERSE_RELATION_TYPE,
                attributes={}
            )
            yield from self.value.create_relation_iterator()


class ScalarTypeMetadata(TypeMetadata):
    def __init__(self,
                 data_type: str,
                 type_str: str,
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(ScalarTypeMetadata, self).__init__(type_str, description, start_label, start_key)
        self.data_type = data_type

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ScalarTypeMetadata):
            return (self.data_type == other.data_type and
                    self.type_str == other.type_str and
                    self.start_label == other.start_label and
                    self.start_key == other.start_key)
        return False

    def is_terminal_type(self) -> bool:
        return True

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if self.description:
            yield self.description.get_node(self.get_description_key())

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if self.description:
            yield self.description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.start_key,
                self.get_description_key()
            )


class StructTypeMetadata(TypeMetadata):
    def __init__(self,
                 struct_items: Dict[str, TypeMetadata],
                 type_str: str,
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(StructTypeMetadata, self).__init__(type_str, description, start_label, start_key)
        self.struct_items = struct_items

        self.kind = 'struct'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, StructTypeMetadata):
            for name, data_type in self.struct_items.items():
                if data_type != other.struct_items[name]:
                    return False
            return (self.type_str == other.type_str and
                    self.start_label == other.start_label and
                    self.start_key == other.start_key)
        return False

    def is_terminal_type(self) -> bool:
        return False

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if self.description:
            yield self.description.get_node(self.get_description_key())

        sort_order = 0
        for name, data_type in self.struct_items.items():
            yield GraphNode(
                key=self.get_node_key(name),
                label=TypeMetadata.NODE_LABEL,
                attributes={
                    TypeMetadata.KIND: self.kind,
                    TypeMetadata.NAME: name,
                    TypeMetadata.DATA_TYPE: data_type.__str__(),
                    TypeMetadata.SORT_ORDER: sort_order
                }
            )
            sort_order += 1

            yield from data_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.start_label:
            raise Exception('Required start node label cannot be None')
        if not self.start_key:
            raise Exception('Required start node key cannot be None')

        if self.description:
            yield self.description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.start_key,
                self.get_description_key()
            )

        for name, data_type in self.struct_items.items():
            yield GraphRelationship(
                start_label=self.start_label,
                start_key=self.start_key,
                end_label=TypeMetadata.NODE_LABEL,
                end_key=self.get_node_key(name),
                type=TypeMetadata.RELATION_TYPE,
                reverse_type=TypeMetadata.INVERSE_RELATION_TYPE,
                attributes={}
            )

            yield from data_type.create_relation_iterator()
