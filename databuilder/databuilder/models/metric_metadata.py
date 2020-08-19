# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from typing import Any, Iterator, Dict, List, Set, Union

# TODO: We could separate TagMetadata from table_metadata to own module
from databuilder.models.table_metadata import TagMetadata
from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, NODE_LABEL, NODE_KEY, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)


NodeTuple = namedtuple('KeyName', ['key', 'name', 'label'])
RelTuple = namedtuple('RelKeys', ['start_label', 'end_label', 'start_key', 'end_key', 'type', 'reverse_type'])


class MetricMetadata(Neo4jCsvSerializable):
    """
    Table metadata that contains columns. It implements Neo4jCsvSerializable so that it can be serialized to produce
    Table, Column and relation of those along with relationship with table and schema. Additionally, it will create
    Database, Cluster, and Schema with relastionships between those.
    These are being created here as it does not make much sense to have different extraction to produce this. As
    database, cluster, schema would be very repititive with low cardinality, it will perform de-dupe so that publisher
    won't need to publish same nodes, relationships.

    This class can be used for both table and view metadata. If it is a View, is_view=True should be passed in.
    """

    DESCRIPTION_NODE_LABEL = 'Description'

    METRIC_NODE_LABEL = 'Metric'
    METRIC_KEY_FORMAT = 'metric://{name}'
    METRIC_NAME = 'name'

    METRIC_DESCRIPTION = 'description'
    METRIC_DESCRIPTION_FORMAT = 'metric://{name}/_description'
    METRIC_DESCRIPTION_RELATION_TYPE = 'DESCRIPTION'
    DESCRIPTION_METRIC_RELATION_TYPE = 'DESCRIPTION_OF'

    DASHBOARD_NODE_LABEL = 'Dashboard'
    DASHBOARD_KEY_FORMAT = '{dashboard_group}://{dashboard_name}'
    DASHBOARD_NAME = 'name'
    DASHBOARD_METRIC_RELATION_TYPE = 'METRIC'
    METRIC_DASHBOARD_RELATION_TYPE = 'METRIC_OF'

    METRIC_TYPE_NODE_LABEL = 'Metrictype'
    METRIC_TYPE_KEY_FORMAT = 'type://{type}'
    METRIC_METRIC_TYPE_RELATION_TYPE = 'METRIC_TYPE'
    METRIC_TYPE_METRIC_RELATION_TYPE = 'METRIC_TYPE_OF'

    # TODO: Idea, maybe move expression from attribute
    # to node or delete commented code below?
    # METRIC_EXPRESSION_NODE_LABEL = 'Metricexpression'
    # METRIC_EXPRESSION_KEY_FORMAT = 'expression://{name}'
    # METRIC_METRIC_EXPRESSION_RELATION_TYPE = 'DEFINITION'
    # METRIC_EXPRESSION_METRIC_RELATION_TYPE = 'DEFINITION_OF'
    METRIC_EXPRESSION_VALUE = 'expression'

    METRIC_TAG_RELATION_TYPE = 'TAG'
    TAG_METRIC_RELATION_TYPE = 'TAG_OF'

    serialized_nodes: Set[Any] = set()
    serialized_rels: Set[Any] = set()

    def __init__(self,
                 dashboard_group: str,
                 dashboard_name: str,
                 name: Union[str, None],
                 expression: str,
                 description: str,
                 type: str,
                 tags: List,
                 ) -> None:

        self.dashboard_group = dashboard_group
        self.dashboard_name = dashboard_name
        self.name = name
        self.expression = expression
        self.description = description
        self.type = type
        self.tags = tags
        self._node_iterator = self._create_next_node()
        self._relation_iterator = self._create_next_relation()

    def __repr__(self) -> str:
        return 'MetricMetadata({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}'.format(
            self.dashboard_group,
            self.dashboard_name,
            self.name,
            self.expression,
            self.description,
            self.type,
            self.tags
        )

    def _get_metric_key(self) -> str:
        return MetricMetadata.METRIC_KEY_FORMAT.format(name=self.name)

    def _get_metric_type_key(self) -> str:
        return MetricMetadata.METRIC_TYPE_KEY_FORMAT.format(type=self.type)

    def _get_dashboard_key(self) -> str:
        return MetricMetadata.DASHBOARD_KEY_FORMAT.format(dashboard_group=self.dashboard_group,
                                                          dashboard_name=self.dashboard_name)

    def _get_metric_description_key(self) -> str:
        return MetricMetadata.METRIC_DESCRIPTION_FORMAT.format(name=self.name)

    def create_next_node(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_next_node(self) -> Iterator[Any]:

        # Metric node
        yield {NODE_LABEL: MetricMetadata.METRIC_NODE_LABEL,
               NODE_KEY: self._get_metric_key(),
               MetricMetadata.METRIC_NAME: self.name,
               MetricMetadata.METRIC_EXPRESSION_VALUE: self.expression
               }

        # Description node
        if self.description:
            yield {NODE_LABEL: MetricMetadata.DESCRIPTION_NODE_LABEL,
                   NODE_KEY: self._get_metric_description_key(),
                   MetricMetadata.METRIC_DESCRIPTION: self.description}

        # Metric tag node
        if self.tags:
            for tag in self.tags:
                yield {NODE_LABEL: TagMetadata.TAG_NODE_LABEL,
                       NODE_KEY: TagMetadata.get_tag_key(tag),
                       TagMetadata.TAG_TYPE: 'metric'}

        # Metric type node
        if self.type:
            yield {NODE_LABEL: MetricMetadata.METRIC_TYPE_NODE_LABEL,
                   NODE_KEY: self._get_metric_type_key(),
                   'name': self.type}

        # FIXME: this logic is wrong and does nothing presently
        others: List[Any] = []

        for node_tuple in others:
            if node_tuple not in MetricMetadata.serialized_nodes:
                MetricMetadata.serialized_nodes.add(node_tuple)
                yield {
                    NODE_LABEL: node_tuple.label,
                    NODE_KEY: node_tuple.key,
                    'name': node_tuple.name
                }

    def create_next_relation(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_next_relation(self) -> Iterator[Any]:

        # Dashboard > Metric relation
        yield {
            RELATION_START_LABEL: MetricMetadata.METRIC_NODE_LABEL,
            RELATION_END_LABEL: MetricMetadata.DASHBOARD_NODE_LABEL,
            RELATION_START_KEY: self._get_metric_key(),
            RELATION_END_KEY: self._get_dashboard_key(),
            RELATION_TYPE: MetricMetadata.METRIC_DASHBOARD_RELATION_TYPE,
            RELATION_REVERSE_TYPE: MetricMetadata.DASHBOARD_METRIC_RELATION_TYPE
        }

        # Metric > Metric description relation
        if self.description:
            yield {
                RELATION_START_LABEL: MetricMetadata.METRIC_NODE_LABEL,
                RELATION_END_LABEL: MetricMetadata.DESCRIPTION_NODE_LABEL,
                RELATION_START_KEY: self._get_metric_key(),
                RELATION_END_KEY: self._get_metric_description_key(),
                RELATION_TYPE: MetricMetadata.METRIC_DESCRIPTION_RELATION_TYPE,
                RELATION_REVERSE_TYPE: MetricMetadata.DESCRIPTION_METRIC_RELATION_TYPE
            }

        # Metric > Metric tag relation
        if self.tags:
            for tag in self.tags:
                yield {
                    RELATION_START_LABEL: MetricMetadata.METRIC_NODE_LABEL,
                    RELATION_END_LABEL: TagMetadata.TAG_NODE_LABEL,
                    RELATION_START_KEY: self._get_metric_key(),
                    RELATION_END_KEY: TagMetadata.get_tag_key(tag),
                    RELATION_TYPE: MetricMetadata.METRIC_TAG_RELATION_TYPE,
                    RELATION_REVERSE_TYPE: MetricMetadata.TAG_METRIC_RELATION_TYPE
                }

        # Metric > Metric type relation
        if self.type:
            yield {
                RELATION_START_LABEL: MetricMetadata.METRIC_NODE_LABEL,
                RELATION_END_LABEL: MetricMetadata.METRIC_TYPE_NODE_LABEL,
                RELATION_START_KEY: self._get_metric_key(),
                RELATION_END_KEY: self._get_metric_type_key(),
                RELATION_TYPE: MetricMetadata.METRIC_METRIC_TYPE_RELATION_TYPE,
                RELATION_REVERSE_TYPE: MetricMetadata.METRIC_TYPE_METRIC_RELATION_TYPE
            }

        # FIXME: this logic is wrong and does nothing presently
        others: List[Any] = []

        for rel_tuple in others:
            if rel_tuple not in MetricMetadata.serialized_rels:
                MetricMetadata.serialized_rels.add(rel_tuple)
                yield {
                    RELATION_START_LABEL: rel_tuple.start_label,
                    RELATION_END_LABEL: rel_tuple.end_label,
                    RELATION_START_KEY: rel_tuple.start_key,
                    RELATION_END_KEY: rel_tuple.end_key,
                    RELATION_TYPE: rel_tuple.type,
                    RELATION_REVERSE_TYPE: rel_tuple.reverse_type
                }
