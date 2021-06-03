# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Any, Iterator, Optional, Union,
)

from databuilder.models.feature.feature_metadata import FeatureMetadata
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable


class FeatureQuery(GraphSerializable):
    NODE_LABEL = 'Feature_Query'

    TEXT_ATTR = 'text'
    LAST_EXECUTED_TIMESTAMP_ATTR = 'last_executed_timestamp'

    FEATURE_QUERY_RELATION_TYPE = 'HAS_QUERY'
    QUERY_FEATURE_RELATION_TYPE = 'QUERY_OF'

    def __init__(self,
                 feature_group: str,
                 feature_name: str,
                 feature_version: str,
                 text: str,
                 last_executed_timestamp: Optional[int] = None,
                 **kwargs: Any
                 ) -> None:

        self.feature_group = feature_group
        self.feature_name = feature_name
        self.feature_version = feature_version
        self.text = text
        self.last_executed_timestamp = last_executed_timestamp

        self._node_iterator = self._create_node_iterator()
        self._relation_iterator = self._create_relation_iterator()

    def __repr__(self) -> str:
        return f'Feature_Query({self.feature_group!r}, {self.feature_name!r}, {self.feature_version!r}, ' \
               f'{self.text!r}, {self.last_executed_timestamp!r})'

    def _get_feature_key(self) -> str:
        return FeatureMetadata.KEY_FORMAT.format(feature_group=self.feature_group,
                                                 name=self.feature_name,
                                                 version=self.feature_version)

    def _get_query_key(self) -> str:
        return f'{self._get_feature_key()}/_query'

    def create_next_node(self) -> Union[GraphNode, None]:
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        attrs = {
            FeatureQuery.TEXT_ATTR: self.text,
        }
        if self.last_executed_timestamp:
            attrs[FeatureQuery.LAST_EXECUTED_TIMESTAMP_ATTR] = self.last_executed_timestamp

        yield GraphNode(
            key=self._get_query_key(),
            label=FeatureQuery.NODE_LABEL,
            attributes=attrs,
        )

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        yield GraphRelationship(
            start_label=FeatureMetadata.NODE_LABEL,
            end_label=FeatureQuery.NODE_LABEL,
            start_key=self._get_feature_key(),
            end_key=self._get_query_key(),
            type=FeatureQuery.FEATURE_QUERY_RELATION_TYPE,
            reverse_type=FeatureQuery.QUERY_FEATURE_RELATION_TYPE,
            attributes={},
        )
