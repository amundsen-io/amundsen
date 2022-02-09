# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import Dict, Iterator, Optional

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
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        self.description = DescriptionMetadata.create_description_metadata(
            source=None,
            text=description
        )
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
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(ArrayTypeMetadata, self).__init__(description,
                                                start_label,
                                                start_key)
        self.data_type = data_type

        self.name = '__array_inner'
        self.kind = 'array'

    def __eq__(self, other) -> bool:
        if isinstance(other, ArrayTypeMetadata):
            return (self.data_type.__eq__(other.data_type)
                    and self.start_label == other.start_label
                    and self.start_key == other.start_key)
        return False

    def __str__(self) -> str:
        return f"{self.kind}<{self.data_type.__str__()}>"

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
                label=TypeMetadata.TYPE_NODE_LABEL,
                attributes={
                    TypeMetadata.TYPE_KIND: self.kind,
                    TypeMetadata.TYPE_DATA_TYPE: self.data_type.__str__()
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
                TypeMetadata.TYPE_NODE_LABEL,
                self.start_key,
                self.get_description_key()
            )

        if not self.is_terminal_type():
            yield GraphRelationship(
                start_label=self.start_label,
                start_key=self.start_key,
                end_label=TypeMetadata.TYPE_NODE_LABEL,
                end_key=self.get_node_key(self.name),
                type=TypeMetadata.TYPE_RELATION_TYPE,
                reverse_type=TypeMetadata.INVERSE_TYPE_RELATION_TYPE,
                attributes={}
            )
            yield from self.data_type.create_relation_iterator()


class MapTypeMetadata(TypeMetadata):
    def __init__(self,
                 key: str,
                 value: TypeMetadata,
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(MapTypeMetadata, self).__init__(description,
                                              start_label,
                                              start_key)
        self.key = key
        self.value = value

        self.name = '__map_inner'
        self.kind = 'map'

    def __eq__(self, other) -> bool:
        if isinstance(other, MapTypeMetadata):
            return (self.key == other.key
                    and self.value.__eq__(other.value)
                    and self.start_label == other.start_label
                    and self.start_key == other.start_key)
        return False

    def __str__(self) -> str:
        return f"{self.kind}<{self.key},{self.value.__str__()}>"

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
                label=TypeMetadata.TYPE_NODE_LABEL,
                attributes={
                    TypeMetadata.TYPE_KIND: self.kind,
                    TypeMetadata.TYPE_MAP_KEY: self.key,
                    TypeMetadata.TYPE_MAP_VALUE: self.value.__str__()
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
                TypeMetadata.TYPE_NODE_LABEL,
                self.start_key,
                self.get_description_key()
            )

        if not self.is_terminal_type():
            yield GraphRelationship(
                start_label=self.start_label,
                start_key=self.start_key,
                end_label=TypeMetadata.TYPE_NODE_LABEL,
                end_key=self.get_node_key(self.name),
                type=TypeMetadata.TYPE_RELATION_TYPE,
                reverse_type=TypeMetadata.INVERSE_TYPE_RELATION_TYPE,
                attributes={}
            )
            yield from self.value.create_relation_iterator()


class ScalarTypeMetadata(TypeMetadata):
    def __init__(self,
                 data_type: str,
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(ScalarTypeMetadata, self).__init__(description,
                                                 start_label,
                                                 start_key)
        self.data_type = data_type

    def __eq__(self, other) -> bool:
        if isinstance(other, ScalarTypeMetadata):
            return (self.data_type == other.data_type
                    and self.start_label == other.start_label
                    and self.start_key == other.start_key)
        return False

    def __str__(self) -> str:
        return self.data_type

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
                TypeMetadata.TYPE_NODE_LABEL,
                self.start_key,
                self.get_description_key()
            )


class StructTypeMetadata(TypeMetadata):
    def __init__(self,
                 struct_items: Dict[str, TypeMetadata],
                 description: Optional[str] = None,
                 start_label: Optional[str] = None,
                 start_key: Optional[str] = None) -> None:
        super(StructTypeMetadata, self).__init__(description,
                                                 start_label,
                                                 start_key)
        self.struct_items = struct_items

        self.kind = 'struct'

    def __eq__(self, other) -> bool:
        if isinstance(other, StructTypeMetadata):
            for name, data_type in self.struct_items.items():
                if data_type != other.struct_items[name]:
                    return False
            return (self.start_label == other.start_label
                    and self.start_key == other.start_key)
        return False

    def __str__(self) -> str:
        inner_string = ''
        for name, data_type in self.struct_items.items():
            inner_string += f"{name}:{data_type.__str__()},"
        return f"{self.kind}<{inner_string[:-1]}>"

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
                label=TypeMetadata.TYPE_NODE_LABEL,
                attributes={
                    TypeMetadata.TYPE_KIND: self.kind,
                    TypeMetadata.TYPE_NAME: name,
                    TypeMetadata.TYPE_DATA_TYPE: data_type.__str__(),
                    TypeMetadata.TYPE_SORT_ORDER: sort_order
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
                TypeMetadata.TYPE_NODE_LABEL,
                self.start_key,
                self.get_description_key()
            )

        for name, data_type in self.struct_items.items():
            yield GraphRelationship(
                start_label=self.start_label,
                start_key=self.start_key,
                end_label=TypeMetadata.TYPE_NODE_LABEL,
                end_key=self.get_node_key(name),
                type=TypeMetadata.TYPE_RELATION_TYPE,
                reverse_type=TypeMetadata.INVERSE_TYPE_RELATION_TYPE,
                attributes={}
            )

            yield from data_type.create_relation_iterator()
