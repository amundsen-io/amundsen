# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Any, Dict, Iterator, List, Optional, Set, Union,
)

from databuilder.models.cluster import cluster_constants
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
# TODO: We could separate TagMetadata from table_metadata to own module
from databuilder.models.table_metadata import TagMetadata


class DashboardMetadata(GraphSerializable):
    """
    Dashboard metadata including dashboard group name, dashboardgroup description, dashboard description,
    and tags.

    Some other metadata e.g. Owners and last-reload/modified times are provided by other models
    e.g. DashboardOwner

    It implements Neo4jCsvSerializable so that it can be serialized to produce
    Dashboard, Tag, Description and relations between those. Additionally, it will create a
    Dashboardgroup with relationships to the Dashboard.
    """
    CLUSTER_KEY_FORMAT = '{product}_dashboard://{cluster}'
    CLUSTER_DASHBOARD_GROUP_RELATION_TYPE = 'DASHBOARD_GROUP'
    DASHBOARD_GROUP_CLUSTER_RELATION_TYPE = 'DASHBOARD_GROUP_OF'

    DASHBOARD_NODE_LABEL = 'Dashboard'
    DASHBOARD_KEY_FORMAT = '{product}_dashboard://{cluster}.{dashboard_group}/{dashboard_name}'
    DASHBOARD_NAME = 'name'
    DASHBOARD_CREATED_TIME_STAMP = 'created_timestamp'
    DASHBOARD_GROUP_URL = 'dashboard_group_url'
    DASHBOARD_URL = 'dashboard_url'

    DASHBOARD_DESCRIPTION_NODE_LABEL = 'Description'
    DASHBOARD_DESCRIPTION = 'description'
    DASHBOARD_DESCRIPTION_FORMAT = \
        '{product}_dashboard://{cluster}.{dashboard_group}/{dashboard_name}/_description'
    DASHBOARD_DESCRIPTION_RELATION_TYPE = 'DESCRIPTION'
    DESCRIPTION_DASHBOARD_RELATION_TYPE = 'DESCRIPTION_OF'

    DASHBOARD_GROUP_NODE_LABEL = 'Dashboardgroup'
    DASHBOARD_GROUP_KEY_FORMAT = '{product}_dashboard://{cluster}.{dashboard_group}'
    DASHBOARD_GROUP_DASHBOARD_RELATION_TYPE = 'DASHBOARD'
    DASHBOARD_DASHBOARD_GROUP_RELATION_TYPE = 'DASHBOARD_OF'

    DASHBOARD_GROUP_DESCRIPTION_KEY_FORMAT = '{product}_dashboard://{cluster}.{dashboard_group}/_description'

    DASHBOARD_TAG_RELATION_TYPE = 'TAG'
    TAG_DASHBOARD_RELATION_TYPE = 'TAG_OF'

    serialized_nodes: Set[Any] = set()
    serialized_rels: Set[Any] = set()

    def __init__(self,
                 dashboard_group: str,
                 dashboard_name: str,
                 description: Union[str, None],
                 tags: List = None,
                 cluster: str = 'gold',
                 product: Optional[str] = '',
                 dashboard_group_id: Optional[str] = None,
                 dashboard_id: Optional[str] = None,
                 dashboard_group_description: Optional[str] = None,
                 created_timestamp: Optional[int] = None,
                 dashboard_group_url: Optional[str] = None,
                 dashboard_url: Optional[str] = None,
                 **kwargs: Any
                 ) -> None:

        self.dashboard_group = dashboard_group
        self.dashboard_name = dashboard_name
        self.dashboard_group_id = dashboard_group_id if dashboard_group_id else dashboard_group
        self.dashboard_id = dashboard_id if dashboard_id else dashboard_name
        self.description = description
        self.tags = tags
        self.product = product
        self.cluster = cluster
        self.dashboard_group_description = dashboard_group_description
        self.created_timestamp = created_timestamp
        self.dashboard_group_url = dashboard_group_url
        self.dashboard_url = dashboard_url
        self._processed_cluster: Set[str] = set()
        self._processed_dashboard_group: Set[str] = set()
        self._node_iterator = self._create_next_node()
        self._relation_iterator = self._create_next_relation()

    def __repr__(self) -> str:
        return f'DashboardMetadata(' \
               f'{self.dashboard_group!r}, {self.dashboard_name!r}, {self.description!r}, {self.tags!r}, ' \
               f'{self.dashboard_group_id!r}, {self.dashboard_id!r}, {self.dashboard_group_description!r}, ' \
               f'{self.created_timestamp!r}, {self.dashboard_group_url!r}, {self.dashboard_url!r})'

    def _get_cluster_key(self) -> str:
        return DashboardMetadata.CLUSTER_KEY_FORMAT.format(cluster=self.cluster,
                                                           product=self.product)

    def _get_dashboard_key(self) -> str:
        return DashboardMetadata.DASHBOARD_KEY_FORMAT.format(dashboard_group=self.dashboard_group_id,
                                                             dashboard_name=self.dashboard_id,
                                                             cluster=self.cluster,
                                                             product=self.product)

    def _get_dashboard_description_key(self) -> str:
        return DashboardMetadata.DASHBOARD_DESCRIPTION_FORMAT.format(dashboard_group=self.dashboard_group_id,
                                                                     dashboard_name=self.dashboard_id,
                                                                     cluster=self.cluster,
                                                                     product=self.product)

    def _get_dashboard_group_description_key(self) -> str:
        return DashboardMetadata.DASHBOARD_GROUP_DESCRIPTION_KEY_FORMAT.format(dashboard_group=self.dashboard_group_id,
                                                                               cluster=self.cluster,
                                                                               product=self.product)

    def _get_dashboard_group_key(self) -> str:
        return DashboardMetadata.DASHBOARD_GROUP_KEY_FORMAT.format(dashboard_group=self.dashboard_group_id,
                                                                   cluster=self.cluster,
                                                                   product=self.product)

    def create_next_node(self) -> Union[GraphNode, None]:
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_next_node(self) -> Iterator[GraphNode]:
        # Cluster node
        if not self._get_cluster_key() in self._processed_cluster:
            self._processed_cluster.add(self._get_cluster_key())
            cluster_node = GraphNode(
                key=self._get_cluster_key(),
                label=cluster_constants.CLUSTER_NODE_LABEL,
                attributes={
                    cluster_constants.CLUSTER_NAME_PROP_KEY: self.cluster
                }
            )
            yield cluster_node

        # Dashboard node attributes
        dashboard_node_attributes: Dict[str, Any] = {
            DashboardMetadata.DASHBOARD_NAME: self.dashboard_name,
        }
        if self.created_timestamp:
            dashboard_node_attributes[DashboardMetadata.DASHBOARD_CREATED_TIME_STAMP] = self.created_timestamp

        if self.dashboard_url:
            dashboard_node_attributes[DashboardMetadata.DASHBOARD_URL] = self.dashboard_url

        dashboard_node = GraphNode(
            key=self._get_dashboard_key(),
            label=DashboardMetadata.DASHBOARD_NODE_LABEL,
            attributes=dashboard_node_attributes
        )

        yield dashboard_node

        # Dashboard group
        if self.dashboard_group and not self._get_dashboard_group_key() in self._processed_dashboard_group:
            self._processed_dashboard_group.add(self._get_dashboard_group_key())
            dashboard_group_node_attributes = {
                DashboardMetadata.DASHBOARD_NAME: self.dashboard_group,
            }

            if self.dashboard_group_url:
                dashboard_group_node_attributes[DashboardMetadata.DASHBOARD_GROUP_URL] = self.dashboard_group_url

            dashboard_group_node = GraphNode(
                key=self._get_dashboard_group_key(),
                label=DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
                attributes=dashboard_group_node_attributes
            )

            yield dashboard_group_node

        # Dashboard group description
        if self.dashboard_group_description:
            dashboard_group_description_node = GraphNode(
                key=self._get_dashboard_group_description_key(),
                label=DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                attributes={
                    DashboardMetadata.DASHBOARD_DESCRIPTION: self.dashboard_group_description
                }
            )
            yield dashboard_group_description_node

        # Dashboard description node
        if self.description:
            dashboard_description_node = GraphNode(
                key=self._get_dashboard_description_key(),
                label=DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                attributes={
                    DashboardMetadata.DASHBOARD_DESCRIPTION: self.description
                }
            )
            yield dashboard_description_node

        # Dashboard tag node
        if self.tags:
            for tag in self.tags:
                dashboard_tag_node = GraphNode(
                    key=TagMetadata.get_tag_key(tag),
                    label=TagMetadata.TAG_NODE_LABEL,
                    attributes={
                        TagMetadata.TAG_TYPE: 'dashboard'
                    }
                )
                yield dashboard_tag_node

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_next_relation(self) -> Iterator[GraphRelationship]:
        # Cluster <-> Dashboard group
        cluster_dashboard_group_relationship = GraphRelationship(
            start_label=cluster_constants.CLUSTER_NODE_LABEL,
            start_key=self._get_cluster_key(),
            end_label=DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
            end_key=self._get_dashboard_group_key(),
            type=DashboardMetadata.CLUSTER_DASHBOARD_GROUP_RELATION_TYPE,
            reverse_type=DashboardMetadata.DASHBOARD_GROUP_CLUSTER_RELATION_TYPE,
            attributes={}
        )
        yield cluster_dashboard_group_relationship

        # Dashboard group > Dashboard group description relation
        if self.dashboard_group_description:
            dashboard_group_description_relationship = GraphRelationship(
                start_label=DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
                start_key=self._get_dashboard_group_key(),
                end_label=DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                end_key=self._get_dashboard_group_description_key(),
                type=DashboardMetadata.DASHBOARD_DESCRIPTION_RELATION_TYPE,
                reverse_type=DashboardMetadata.DESCRIPTION_DASHBOARD_RELATION_TYPE,
                attributes={}
            )
            yield dashboard_group_description_relationship

        # Dashboard group > Dashboard relation
        dashboard_group_dashboard_relationship = GraphRelationship(
            start_label=DashboardMetadata.DASHBOARD_NODE_LABEL,
            end_label=DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
            start_key=self._get_dashboard_key(),
            end_key=self._get_dashboard_group_key(),
            type=DashboardMetadata.DASHBOARD_DASHBOARD_GROUP_RELATION_TYPE,
            reverse_type=DashboardMetadata.DASHBOARD_GROUP_DASHBOARD_RELATION_TYPE,
            attributes={}
        )
        yield dashboard_group_dashboard_relationship

        # Dashboard > Dashboard description relation
        if self.description:
            dashboard_description_relationship = GraphRelationship(
                start_label=DashboardMetadata.DASHBOARD_NODE_LABEL,
                end_label=DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                start_key=self._get_dashboard_key(),
                end_key=self._get_dashboard_description_key(),
                type=DashboardMetadata.DASHBOARD_DESCRIPTION_RELATION_TYPE,
                reverse_type=DashboardMetadata.DESCRIPTION_DASHBOARD_RELATION_TYPE,
                attributes={}
            )
            yield dashboard_description_relationship

        # Dashboard > Dashboard tag relation
        if self.tags:
            for tag in self.tags:
                dashboard_tag_relationship = GraphRelationship(
                    start_label=DashboardMetadata.DASHBOARD_NODE_LABEL,
                    end_label=TagMetadata.TAG_NODE_LABEL,
                    start_key=self._get_dashboard_key(),
                    end_key=TagMetadata.get_tag_key(tag),
                    type=DashboardMetadata.DASHBOARD_TAG_RELATION_TYPE,
                    reverse_type=DashboardMetadata.TAG_DASHBOARD_RELATION_TYPE,
                    attributes={}
                )
                yield dashboard_tag_relationship
