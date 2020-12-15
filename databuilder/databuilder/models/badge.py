# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import re
from typing import List, Optional

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable


class Badge:
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category

    def __repr__(self) -> str:
        return f'Badge({self.name!r}, {self.category!r})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Badge):
            return NotImplemented
        return self.name == other.name and \
            self.category == other.category


class BadgeMetadata(GraphSerializable):
    """
    Badge model.
    """
    BADGE_NODE_LABEL = 'Badge'
    BADGE_KEY_FORMAT = '{badge}'
    BADGE_CATEGORY = 'category'

    # Relation between entity and badge
    BADGE_RELATION_TYPE = 'HAS_BADGE'
    INVERSE_BADGE_RELATION_TYPE = 'BADGE_FOR'

    def __init__(self,
                 start_label: str,  # Table, Dashboard, Column
                 start_key: str,
                 badges: List[Badge],
                 ):
        self.badges = badges

        table_key_pattern = re.compile('[a-z]+://[a-zA-Z0-9_.-]+.[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+')
        dashboard_key_pattern = re.compile('[a-z]+_dashboard://[a-zA-Z0-9_.-]+.[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+')
        column_key_pattern = re.compile('[a-z]+://[a-zA-Z0-9_.-]+.[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+')
        map_label_to_key_pattern = {
            'Table': table_key_pattern,
            'Dashboard': dashboard_key_pattern,
            'Column': column_key_pattern,
        }
        if start_label in map_label_to_key_pattern.keys():
            self.start_label = start_label
            if map_label_to_key_pattern[start_label].match(start_key):
                self.start_key = start_key
            else:
                raise Exception(start_key + ' does not match the key pattern for a ' + start_label)
        else:
            raise Exception(start_label + ' is not a valid start_label for a Badge relation')

        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def __repr__(self) -> str:
        return f'BadgeMetadata({self.start_label!r}, {self.start_key!r})'

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

    @staticmethod
    def get_badge_key(name: str) -> str:
        if not name:
            return ''
        return BadgeMetadata.BADGE_KEY_FORMAT.format(badge=name)

    def get_metadata_model_key(self) -> str:
        return self.start_key

    def create_nodes(self) -> List[GraphNode]:
        """
        Create a list of `GraphNode` records
        :return:
        """
        results = []
        for badge in self.badges:
            if badge:
                node = GraphNode(
                    key=self.get_badge_key(badge.name),
                    label=self.BADGE_NODE_LABEL,
                    attributes={
                        self.BADGE_CATEGORY: badge.category
                    }
                )
                results.append(node)
        return results

    def create_relation(self) -> List[GraphRelationship]:
        results: List[GraphRelationship] = []
        for badge in self.badges:
            relation = GraphRelationship(
                start_label=self.start_label,
                end_label=self.BADGE_NODE_LABEL,
                start_key=self.start_key,
                end_key=self.get_badge_key(badge.name),
                type=self.BADGE_RELATION_TYPE,
                reverse_type=self.INVERSE_BADGE_RELATION_TYPE,
                attributes={}
            )
            results.append(relation)
        return results
