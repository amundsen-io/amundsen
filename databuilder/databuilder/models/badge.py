# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, Optional
import re

from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable, NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


class Badge:
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category

    def __repr__(self) -> str:
        return 'Badge({!r}, {!r})'.format(self.name,
                                          self.category)


class BadgeMetadata(Neo4jCsvSerializable):
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
        return 'BadgeMetadata({!r}, {!r})'.format(self.start_label,
                                                  self.start_key)

    def create_next_node(self) -> Optional[Dict[str, Any]]:
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[Dict[str, Any]]:
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

    def create_nodes(self) -> List[Dict[str, Any]]:
        """
        Create a list of Neo4j node records
        :return:
        """
        results = []
        for badge in self.badges:
            if badge:
                results.append({
                    NODE_KEY: self.get_badge_key(badge.name),
                    NODE_LABEL: self.BADGE_NODE_LABEL,
                    self.BADGE_CATEGORY: badge.category
                })
        return results

    def create_relation(self) -> List[Dict[str, Any]]:
        results = []
        for badge in self.badges:
            results.append({
                RELATION_START_LABEL: self.start_label,
                RELATION_END_LABEL: self.BADGE_NODE_LABEL,
                RELATION_START_KEY: self.start_key,
                RELATION_END_KEY: self.get_badge_key(badge.name),
                RELATION_TYPE: self.BADGE_RELATION_TYPE,
                RELATION_REVERSE_TYPE: self.INVERSE_BADGE_RELATION_TYPE,
            })
        return results
