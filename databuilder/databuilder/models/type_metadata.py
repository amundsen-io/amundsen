# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
import logging
from typing import (
    Any, Dict, Iterator, List, Optional, Union,
)

from databuilder.models.badge import Badge, BadgeMetadata
from databuilder.models.description_metadata import DescriptionMetadata
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import ColumnMetadata, _format_as_list

LOGGER = logging.getLogger(__name__)


class TypeMetadata(abc.ABC, GraphSerializable):
    NODE_LABEL = 'Type_Metadata'
    COL_TM_RELATION_TYPE = 'TYPE_METADATA'
    TM_COL_RELATION_TYPE = 'TYPE_METADATA_OF'
    SUBTYPE_RELATION_TYPE = 'SUBTYPE'
    INVERSE_SUBTYPE_RELATION_TYPE = 'SUBTYPE_OF'
    KIND = 'kind'
    NAME = 'name'
    DATA_TYPE = 'data_type'
    SORT_ORDER = 'sort_order'

    @abc.abstractmethod
    def __init__(self,
                 name: str,
                 parent: Union[ColumnMetadata, 'TypeMetadata'],
                 type_str: str,
                 sort_order: Optional[int] = None) -> None:
        self.name = name
        self.parent = parent
        self.type_str = type_str
        # Sort order among TypeMetadata objects with the same parent
        self.sort_order = sort_order

        self._description: Optional[DescriptionMetadata] = None
        self._badges: Optional[List[Badge]] = None

        self._node_iter = self.create_node_iterator()
        self._relation_iter = self.create_relation_iterator()

    def get_description(self) -> Optional[DescriptionMetadata]:
        return self._description

    def set_description(self, description: str) -> None:
        if isinstance(self.parent, ColumnMetadata):
            LOGGER.warning("""Frontend does not currently support setting descriptions for type metadata
                           objects with a ColumnMetadata parent, since the top level type metadata does
                           not have its own row in the column table""")
        elif isinstance(self.parent, ArrayTypeMetadata):
            LOGGER.warning("""Frontend does not currently support setting descriptions for type metadata
                           objects with an ArrayTypeMetadata parent, since this level in the nesting
                           hierarchy is not named and therefore is represented by short row that is not
                           clickable""")
        else:
            self._description = DescriptionMetadata.create_description_metadata(
                source=None,
                text=description
            )

    def get_badges(self) -> Optional[List[Badge]]:
        return self._badges

    def set_badges(self, badges: Union[List[str], None] = None) -> None:
        if isinstance(self.parent, ColumnMetadata):
            LOGGER.warning("""Frontend does not currently support setting badges for type metadata
                           objects with a ColumnMetadata parent, since the top level type metadata does
                           not have its own row in the column table""")
        elif isinstance(self.parent, ArrayTypeMetadata):
            LOGGER.warning("""Frontend does not currently support setting badges for type metadata
                           objects with an ArrayTypeMetadata parent, since this level in the nesting
                           hierarchy is not named and therefore is represented by short row that is not
                           clickable""")
        else:
            formatted_badges = _format_as_list(badges)
            self._badges = [Badge(badge, 'type_metadata') for badge in formatted_badges]

    @abc.abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def is_terminal_type(self) -> bool:
        """
        This is used to determine whether any child nodes
        should be created for the associated TypeMetadata object.
        """
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
        return f"{self.parent_key()}/{self.name}"

    def description_key(self) -> Optional[str]:
        if self._description:
            description_id = self._description.get_description_id()
            return f"{self.key()}/{description_id}"
        return None

    def relation_type(self) -> str:
        if isinstance(self.parent, ColumnMetadata):
            return TypeMetadata.COL_TM_RELATION_TYPE
        return TypeMetadata.SUBTYPE_RELATION_TYPE

    def inverse_relation_type(self) -> str:
        if isinstance(self.parent, ColumnMetadata):
            return TypeMetadata.TM_COL_RELATION_TYPE
        return TypeMetadata.INVERSE_SUBTYPE_RELATION_TYPE

    def parent_key(self) -> str:
        if isinstance(self.parent, ColumnMetadata):
            column_key = self.parent.get_column_key()
            assert column_key is not None, f"Column key must be set for {self.parent.name}"
            return column_key
        return self.parent.key()

    def parent_label(self) -> str:
        if isinstance(self.parent, ColumnMetadata):
            return ColumnMetadata.COLUMN_NODE_LABEL
        return TypeMetadata.NODE_LABEL

    def __repr__(self) -> str:
        return f"TypeMetadata({self.type_str!r})"


class ArrayTypeMetadata(TypeMetadata):
    kind = 'array'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(ArrayTypeMetadata, self).__init__(*args, **kwargs)
        self.array_inner_type: Optional[TypeMetadata] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ArrayTypeMetadata):
            return (self.name == other.name and
                    self.type_str == other.type_str and
                    self.sort_order == other.sort_order and
                    self._description == other._description and
                    self._badges == other._badges and
                    self.array_inner_type == other.array_inner_type and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return not self.array_inner_type

    def create_node_iterator(self) -> Iterator[GraphNode]:
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

        if self._description:
            description_key = self.description_key()
            assert description_key is not None, f"Could not retrieve description key for {self.name}"
            yield self._description.get_node(description_key)

        if self._badges:
            badge_metadata = BadgeMetadata(start_label=TypeMetadata.NODE_LABEL,
                                           start_key=self.key(),
                                           badges=self._badges)
            badge_nodes = badge_metadata.get_badge_nodes()
            for node in badge_nodes:
                yield node

        if not self.is_terminal_type():
            assert self.array_inner_type is not None, f"Array inner type must be set for {self.name}"
            yield from self.array_inner_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        yield GraphRelationship(
            start_label=self.parent_label(),
            start_key=self.parent_key(),
            end_label=TypeMetadata.NODE_LABEL,
            end_key=self.key(),
            type=self.relation_type(),
            reverse_type=self.inverse_relation_type(),
            attributes={}
        )

        if self._description:
            description_key = self.description_key()
            assert description_key is not None, f"Could not retrieve description key for {self.name}"
            yield self._description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.key(),
                description_key
            )

        if self._badges:
            badge_metadata = BadgeMetadata(start_label=TypeMetadata.NODE_LABEL,
                                           start_key=self.key(),
                                           badges=self._badges)
            badge_relations = badge_metadata.get_badge_relations()
            for relation in badge_relations:
                yield relation

        if not self.is_terminal_type():
            assert self.array_inner_type is not None, f"Array inner type must be set for {self.name}"
            yield from self.array_inner_type.create_relation_iterator()


class MapTypeMetadata(TypeMetadata):
    kind = 'map'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(MapTypeMetadata, self).__init__(*args, **kwargs)
        self.map_key_type: Optional[TypeMetadata] = None
        self.map_value_type: Optional[TypeMetadata] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MapTypeMetadata):
            return (self.name == other.name and
                    self.map_key_type == other.map_key_type and
                    self.map_value_type == other.map_value_type and
                    self.type_str == other.type_str and
                    self.sort_order == other.sort_order and
                    self._description == other._description and
                    self._badges == other._badges and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return not self.map_key_type or not self.map_value_type

    def create_node_iterator(self) -> Iterator[GraphNode]:
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

        if self._description:
            description_key = self.description_key()
            assert description_key is not None, f"Could not retrieve description key for {self.name}"
            yield self._description.get_node(description_key)

        if self._badges:
            badge_metadata = BadgeMetadata(start_label=TypeMetadata.NODE_LABEL,
                                           start_key=self.key(),
                                           badges=self._badges)
            badge_nodes = badge_metadata.get_badge_nodes()
            for node in badge_nodes:
                yield node

        if not self.is_terminal_type():
            assert self.map_key_type is not None, f"Map key type must be set for {self.name}"
            assert self.map_value_type is not None, f"Map value type must be set for {self.name}"
            yield from self.map_key_type.create_node_iterator()
            yield from self.map_value_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        yield GraphRelationship(
            start_label=self.parent_label(),
            start_key=self.parent_key(),
            end_label=TypeMetadata.NODE_LABEL,
            end_key=self.key(),
            type=self.relation_type(),
            reverse_type=self.inverse_relation_type(),
            attributes={}
        )

        if self._description:
            description_key = self.description_key()
            assert description_key is not None, f"Could not retrieve description key for {self.name}"
            yield self._description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.key(),
                description_key
            )

        if self._badges:
            badge_metadata = BadgeMetadata(start_label=TypeMetadata.NODE_LABEL,
                                           start_key=self.key(),
                                           badges=self._badges)
            badge_relations = badge_metadata.get_badge_relations()
            for relation in badge_relations:
                yield relation

        if not self.is_terminal_type():
            assert self.map_key_type is not None, f"Map key type must be set for {self.name}"
            assert self.map_value_type is not None, f"Map value type must be set for {self.name}"
            yield from self.map_key_type.create_relation_iterator()
            yield from self.map_value_type.create_relation_iterator()


class ScalarTypeMetadata(TypeMetadata):
    """
    ScalarTypeMetadata represents any non complex type that does not
    require special handling. It is also used as the default TypeMetadata
    class when a type string cannot be parsed.
    """
    kind = 'scalar'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(ScalarTypeMetadata, self).__init__(*args, **kwargs)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ScalarTypeMetadata):
            return (self.name == other.name and
                    self.type_str == other.type_str and
                    self.sort_order == other.sort_order and
                    self._description == other._description and
                    self._badges == other._badges and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return True

    def create_node_iterator(self) -> Iterator[GraphNode]:
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

        if self._description:
            description_key = self.description_key()
            assert description_key is not None, f"Could not retrieve description key for {self.name}"
            yield self._description.get_node(description_key)

        if self._badges:
            badge_metadata = BadgeMetadata(start_label=TypeMetadata.NODE_LABEL,
                                           start_key=self.key(),
                                           badges=self._badges)
            badge_nodes = badge_metadata.get_badge_nodes()
            for node in badge_nodes:
                yield node

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        yield GraphRelationship(
            start_label=self.parent_label(),
            start_key=self.parent_key(),
            end_label=TypeMetadata.NODE_LABEL,
            end_key=self.key(),
            type=self.relation_type(),
            reverse_type=self.inverse_relation_type(),
            attributes={}
        )

        if self._description:
            description_key = self.description_key()
            assert description_key is not None, f"Could not retrieve description key for {self.name}"
            yield self._description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.key(),
                description_key
            )

        if self._badges:
            badge_metadata = BadgeMetadata(start_label=TypeMetadata.NODE_LABEL,
                                           start_key=self.key(),
                                           badges=self._badges)
            badge_relations = badge_metadata.get_badge_relations()
            for relation in badge_relations:
                yield relation


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
                    self.sort_order == other.sort_order and
                    self._description == other._description and
                    self._badges == other._badges and
                    self.key() == other.key())
        return False

    def is_terminal_type(self) -> bool:
        return not self.struct_items

    def create_node_iterator(self) -> Iterator[GraphNode]:
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

        if self._description:
            description_key = self.description_key()
            assert description_key is not None, f"Could not retrieve description key for {self.name}"
            yield self._description.get_node(description_key)

        if self._badges:
            badge_metadata = BadgeMetadata(start_label=TypeMetadata.NODE_LABEL,
                                           start_key=self.key(),
                                           badges=self._badges)
            badge_nodes = badge_metadata.get_badge_nodes()
            for node in badge_nodes:
                yield node

        if not self.is_terminal_type():
            assert self.struct_items, f"Struct items must be set for {self.name}"
            for name, data_type in self.struct_items.items():
                yield from data_type.create_node_iterator()

    def create_relation_iterator(self) -> Iterator[GraphRelationship]:
        yield GraphRelationship(
            start_label=self.parent_label(),
            start_key=self.parent_key(),
            end_label=TypeMetadata.NODE_LABEL,
            end_key=self.key(),
            type=self.relation_type(),
            reverse_type=self.inverse_relation_type(),
            attributes={}
        )

        if self._description:
            description_key = self.description_key()
            assert description_key is not None, f"Could not retrieve description key for {self.name}"
            yield self._description.get_relation(
                TypeMetadata.NODE_LABEL,
                self.key(),
                description_key
            )

        if self._badges:
            badge_metadata = BadgeMetadata(start_label=TypeMetadata.NODE_LABEL,
                                           start_key=self.key(),
                                           badges=self._badges)
            badge_relations = badge_metadata.get_badge_relations()
            for relation in badge_relations:
                yield relation

        if not self.is_terminal_type():
            assert self.struct_items, f"Struct items must be set for {self.name}"
            for name, data_type in self.struct_items.items():
                yield from data_type.create_relation_iterator()
