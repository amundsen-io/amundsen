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
    DATA_TYPE = 'data_type'
    MAP_KEY = 'map_key'
    MAP_VALUE = 'map_value'
    SORT_ORDER = 'sort_order'

    @abc.abstractmethod
    def __init__(self,
                 name: str,
                 parent: Union[ColumnMetadata, 'TypeMetadata'],
                 type_str: str,
                 description: Optional[str] = None) -> None:
        self.name = name
        self.parent = parent
        self.type_str = type_str
        self.description = DescriptionMetadata.create_description_metadata(
            source=None,
            text=description
        )
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
        if isinstance(self.parent, ColumnMetadata):
            return f"{self.parent_key()}/type/{self.name}"
        else:
            return f"{self.parent_key()}/{self.name}"

    def description_key(self) -> str:
        if self.description:
            description_id = self.description.get_description_id()
            return f"{self.key()}/{description_id}"
        else:
            return ''

    def parent_key(self) -> str:
        if isinstance(self.parent, ColumnMetadata):
            column_key = self.parent.get_column_key()
            return column_key if column_key else ''
        else:
            return self.parent.key()

    def parent_label(self) -> str:
        if isinstance(self.parent, ColumnMetadata):
            return ColumnMetadata.COLUMN_NODE_LABEL
        else:
            return TypeMetadata.NODE_LABEL

    def __repr__(self) -> str:
        return f"TypeMetadata({self.type_str!r})"


class ArrayTypeMetadata(TypeMetadata):
    kind = 'array'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(ArrayTypeMetadata, self).__init__(*args, **kwargs)
        self.data_type: Optional[TypeMetadata] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ArrayTypeMetadata):
            return (self.name == other.name and
                    self.type_str == other.type_str and
                    self.description == other.description and
                    self.sort_order == other.sort_order and
                    self.data_type == other.data_type and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return isinstance(self.data_type, ScalarTypeMetadata)

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')
        if not self.data_type:
            raise Exception('Must set inner data type')

        node_attributes: Dict[str, Union[str, None, int]] = {
            TypeMetadata.KIND: self.kind,
            TypeMetadata.NAME: self.name,
            TypeMetadata.DATA_TYPE: self.data_type.type_str
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
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')
        if not self.data_type:
            raise Exception('Must set inner data type')

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
    kind = 'map'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(MapTypeMetadata, self).__init__(*args, **kwargs)
        self.map_key: Optional[TypeMetadata] = None
        self.data_type: Optional[TypeMetadata] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MapTypeMetadata):
            return (self.name == other.name and
                    self.map_key == other.map_key and
                    self.data_type == other.data_type and
                    self.type_str == other.type_str and
                    self.description == other.description and
                    self.sort_order == other.sort_order and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return False

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')
        if not self.map_key:
            raise Exception('Must set map key')
        if not self.data_type:
            raise Exception('Must set inner data type')

        node_attributes: Dict[str, Union[str, None, int]] = {
            TypeMetadata.KIND: self.kind,
            TypeMetadata.NAME: self.name,
            TypeMetadata.MAP_KEY: self.map_key.type_str,
            TypeMetadata.MAP_VALUE: self.data_type.type_str
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
        yield from self.data_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')
        if not self.map_key:
            raise Exception('Must set map key')
        if not self.data_type:
            raise Exception('Must set inner data type')

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
        yield from self.data_type.create_relation_iterator()


class ScalarTypeMetadata(TypeMetadata):
    kind = 'scalar'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(ScalarTypeMetadata, self).__init__(*args, **kwargs)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ScalarTypeMetadata):
            return (self.name == other.name and
                    self.type_str == other.type_str and
                    self.description == other.description and
                    self.sort_order == other.sort_order and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return True

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')

        node_attributes: Dict[str, Union[str, None, int]] = {
            TypeMetadata.KIND: self.kind,
            TypeMetadata.NAME: self.name,
            TypeMetadata.DATA_TYPE: self.type_str
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
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')

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
    kind = 'struct'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(StructTypeMetadata, self).__init__(*args, **kwargs)
        self.struct_items: Optional[Dict[str, TypeMetadata]] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, StructTypeMetadata):

            return (self.name == other.name and
                    self.struct_items == other.struct_items and
                    self.type_str == other.type_str and
                    self.description == other.description and
                    self.sort_order == other.sort_order and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return False

    def create_node_iterator(self) -> Iterator[GraphNode]:
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')

        node_attributes: Dict[str, Union[str, None, int]] = {
            TypeMetadata.KIND: self.kind,
            TypeMetadata.NAME: self.name,
            TypeMetadata.DATA_TYPE: self.type_str
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

        if self.struct_items:
            for name, data_type in self.struct_items.items():
                yield from data_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if not self.parent_key():
            raise Exception('Required parent node key cannot be None')

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

        if self.struct_items:
            for name, data_type in self.struct_items.items():
                yield from data_type.create_relation_iterator()
