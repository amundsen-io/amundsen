# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import (
    Any, Dict, Iterator, Optional, Union,
)

from databuilder.models.description_metadata import DescriptionMetadata
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import ColumnMetadata


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
                 description: Optional[str] = None) -> None:
        self.type_str = type_str
        self.description = DescriptionMetadata.create_description_metadata(
            source=None,
            text=description
        )

        self.name: Optional[str] = None
        self.parent: Union[ColumnMetadata, TypeMetadata, None] = None
        self.sort_order: Optional[int] = None

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

    def key(self) -> str:
        parent_key = self.parent_key()
        if not parent_key or not self.name:
            return ''
        else:
            return f"{parent_key}/{self.name}"

    def description_key(self) -> str:
        key = self.key()
        if not self.description or not key:
            return ''
        else:
            description_id = self.description.get_description_id()
            return f"{key}/{description_id}"

    def parent_key(self) -> str:
        if not self.parent:
            return ''
        elif isinstance(self.parent, ColumnMetadata):
            return self.parent.column_key if self.parent.column_key else ''
        else:
            return self.parent.key()

    def parent_label(self) -> str:
        if not self.parent:
            return ''
        if isinstance(self.parent, ColumnMetadata):
            return ColumnMetadata.COLUMN_NODE_LABEL
        else:
            return TypeMetadata.NODE_LABEL


class ArrayTypeMetadata(TypeMetadata):
    def __init__(self,
                 data_type: TypeMetadata,
                 type_str: str,
                 description: Optional[str] = None) -> None:
        super(ArrayTypeMetadata, self).__init__(type_str, description)
        self.data_type = data_type

        self.kind = 'array'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ArrayTypeMetadata):
            return (self.data_type == other.data_type and
                    self.type_str == other.type_str and
                    self.description == other.description and
                    self.name == other.name and
                    self.sort_order == other.sort_order and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return isinstance(self.data_type, ScalarTypeMetadata)

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.key():
            raise Exception('Required node key cannot be None')

        node_attributes: Dict[str, Union[str, None, int]] = {
            TypeMetadata.KIND: self.kind,
            TypeMetadata.NAME: self.name,
            TypeMetadata.DATA_TYPE: self.data_type.__str__()
        }

        if isinstance(self.sort_order, int):
            node_attributes[TypeMetadata.SORT_ORDER] = self.sort_order

        yield GraphNode(
            key=self.key(),
            label=TypeMetadata.NODE_LABEL,
            attributes=node_attributes
        )

        if self.description:
            yield self.description.get_node(self.description_key())

        if not self.is_terminal_type():
            yield from self.data_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.parent_label():
            raise Exception('Required parent node label cannot be None')
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')
        if not self.key():
            raise Exception('Required node key cannot be None')

        yield GraphRelationship(
            start_label=self.parent_label(),
            start_key=self.parent_key(),
            end_label=TypeMetadata.NODE_LABEL,
            end_key=self.key(),
            type=TypeMetadata.RELATION_TYPE,
            reverse_type=TypeMetadata.INVERSE_RELATION_TYPE,
            attributes={}
        )

        if self.description:
            yield self.description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.key(),
                self.description_key()
            )

        if not self.is_terminal_type():
            yield from self.data_type.create_relation_iterator()


class MapTypeMetadata(TypeMetadata):
    def __init__(self,
                 map_key: TypeMetadata,
                 map_value: TypeMetadata,
                 type_str: str,
                 description: Optional[str] = None) -> None:
        super(MapTypeMetadata, self).__init__(type_str, description)
        self.map_key = map_key
        self.map_value = map_value

        self.kind = 'map'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MapTypeMetadata):
            return (self.map_key == other.map_key and
                    self.map_value == other.map_value and
                    self.type_str == other.type_str and
                    self.description == other.description and
                    self.name == other.name and
                    self.sort_order == other.sort_order and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return False

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.key():
            raise Exception('Required node key cannot be None')

        node_attributes: Dict[str, Union[str, None, int]] = {
            TypeMetadata.KIND: self.kind,
            TypeMetadata.NAME: self.name,
            TypeMetadata.MAP_KEY: self.map_key.__str__(),
            TypeMetadata.MAP_VALUE: self.map_value.__str__()
        }

        if isinstance(self.sort_order, int):
            node_attributes[TypeMetadata.SORT_ORDER] = self.sort_order

        yield GraphNode(
            key=self.key(),
            label=TypeMetadata.NODE_LABEL,
            attributes=node_attributes
        )

        if self.description:
            yield self.description.get_node(self.description_key())

        yield from self.map_key.create_node_iterator()
        yield from self.map_value.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.parent_label():
            raise Exception('Required parent node label cannot be None')
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')
        if not self.key():
            raise Exception('Required node key cannot be None')

        yield GraphRelationship(
            start_label=self.parent_label(),
            start_key=self.parent_key(),
            end_label=TypeMetadata.NODE_LABEL,
            end_key=self.key(),
            type=TypeMetadata.RELATION_TYPE,
            reverse_type=TypeMetadata.INVERSE_RELATION_TYPE,
            attributes={}
        )

        if self.description:
            yield self.description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.key(),
                self.description_key()
            )

        yield from self.map_key.create_relation_iterator()
        yield from self.map_value.create_relation_iterator()


class ScalarTypeMetadata(TypeMetadata):
    def __init__(self,
                 data_type: str,
                 type_str: str,
                 description: Optional[str] = None) -> None:
        super(ScalarTypeMetadata, self).__init__(type_str, description)
        self.data_type = data_type

        self.kind = 'scalar'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ScalarTypeMetadata):
            return (self.data_type == other.data_type and
                    self.type_str == other.type_str and
                    self.description == other.description and
                    self.name == other.name and
                    self.sort_order == other.sort_order and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return True

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.key():
            raise Exception('Required node key cannot be None')

        node_attributes: Dict[str, Union[str, None, int]] = {
            TypeMetadata.KIND: self.kind,
            TypeMetadata.NAME: self.name,
            TypeMetadata.DATA_TYPE: self.__str__()
        }

        if isinstance(self.sort_order, int):
            node_attributes[TypeMetadata.SORT_ORDER] = self.sort_order

        yield GraphNode(
            key=self.key(),
            label=TypeMetadata.NODE_LABEL,
            attributes=node_attributes
        )

        if self.description:
            yield self.description.get_node(self.description_key())

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.parent_label():
            raise Exception('Required parent node label cannot be None')
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')
        if not self.key():
            raise Exception('Required node key cannot be None')

        yield GraphRelationship(
            start_label=self.parent_label(),
            start_key=self.parent_key(),
            end_label=TypeMetadata.NODE_LABEL,
            end_key=self.key(),
            type=TypeMetadata.RELATION_TYPE,
            reverse_type=TypeMetadata.INVERSE_RELATION_TYPE,
            attributes={}
        )

        if self.description:
            yield self.description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.key(),
                self.description_key()
            )


class StructTypeMetadata(TypeMetadata):
    def __init__(self,
                 struct_items: Dict[str, TypeMetadata],
                 type_str: str,
                 description: Optional[str] = None) -> None:
        super(StructTypeMetadata, self).__init__(type_str, description)
        self.struct_items = struct_items

        self.kind = 'struct'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, StructTypeMetadata):
            for name, data_type in self.struct_items.items():
                if data_type != other.struct_items[name]:
                    return False
            return (self.type_str == other.type_str and
                    self.description == other.description and
                    self.name == other.name and
                    self.sort_order == other.sort_order and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return False

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.key():
            raise Exception('Required node key cannot be None')

        node_attributes: Dict[str, Union[str, None, int]] = {
            TypeMetadata.KIND: self.kind,
            TypeMetadata.NAME: self.name,
            TypeMetadata.DATA_TYPE: self.__str__()
        }

        if isinstance(self.sort_order, int):
            node_attributes[TypeMetadata.SORT_ORDER] = self.sort_order

        yield GraphNode(
            key=self.key(),
            label=TypeMetadata.NODE_LABEL,
            attributes=node_attributes
        )

        if self.description:
            yield self.description.get_node(self.description_key())

        for name, data_type in self.struct_items.items():
            yield from data_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.parent_label():
            raise Exception('Required parent node label cannot be None')
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')
        if not self.key():
            raise Exception('Required node key cannot be None')

        yield GraphRelationship(
            start_label=self.parent_label(),
            start_key=self.parent_key(),
            end_label=TypeMetadata.NODE_LABEL,
            end_key=self.key(),
            type=TypeMetadata.RELATION_TYPE,
            reverse_type=TypeMetadata.INVERSE_RELATION_TYPE,
            attributes={}
        )

        if self.description:
            yield self.description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.key(),
                self.description_key()
            )

        for name, data_type in self.struct_items.items():
            yield from data_type.create_relation_iterator()
