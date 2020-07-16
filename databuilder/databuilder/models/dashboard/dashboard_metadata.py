# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from typing import Any, Union, Iterator, Dict, Set, Optional  # noqa: F401

from databuilder.models.cluster import cluster_constants
from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, NODE_LABEL, NODE_KEY, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)
# TODO: We could separate TagMetadata from table_metadata to own module
from databuilder.models.table_metadata import TagMetadata

NodeTuple = namedtuple('KeyName', ['key', 'name', 'label'])
RelTuple = namedtuple('RelKeys', ['start_label', 'end_label', 'start_key', 'end_key', 'type', 'reverse_type'])


class DashboardMetadata(Neo4jCsvSerializable):
    """
    Dashboard metadata that contains dashboard group name, dashboardgroup description, dashboard description,
    along with tags, owner userid and lastreloadtime.
    (Owner ID and last reload time will be supported by separate Extractor later on with more information)

    It implements Neo4jCsvSerializable so that it can be serialized to produce
    Dashboard, Tag, Description, Lastreloadtime and relation of those. Additionally, it will create
    Dashboardgroup with relationships to Dashboard. If users exist in neo4j, it will create
    the relation between dashboard and user (owner).

    Lastreloadtime is the time when the Dashboard was last reloaded.
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

    serialized_nodes = set()  # type: Set[Any]
    serialized_rels = set()  # type: Set[Any]

    def __init__(self,
                 dashboard_group,  # type: str
                 dashboard_name,  # type: str
                 description,  # type: Union[str, None]
                 tags=None,  # type: List
                 cluster='gold',  # type: str
                 product='',  # type: Optional[str]
                 dashboard_group_id=None,  # type: Optional[str]
                 dashboard_id=None,  # type: Optional[str]
                 dashboard_group_description=None,  # type: Optional[str]
                 created_timestamp=None,  # type: Optional[int]
                 dashboard_group_url=None,  # type: Optional[str]
                 dashboard_url=None,  # type: Optional[str]
                 **kwargs
                 ):
        # type: (...) -> None

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
        self._processed_cluster = set()
        self._processed_dashboard_group = set()
        self._node_iterator = self._create_next_node()
        self._relation_iterator = self._create_next_relation()

    def __repr__(self):
        # type: () -> str
        return 'DashboardMetadata({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r})' \
            .format(self.dashboard_group,
                    self.dashboard_name,
                    self.description,
                    self.tags,
                    self.dashboard_group_id,
                    self.dashboard_id,
                    self.dashboard_group_description,
                    self.created_timestamp,
                    self.dashboard_group_url,
                    self.dashboard_url,
                    )

    def _get_cluster_key(self):
        # type: () -> str
        return DashboardMetadata.CLUSTER_KEY_FORMAT.format(cluster=self.cluster,
                                                           product=self.product)

    def _get_dashboard_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_KEY_FORMAT.format(dashboard_group=self.dashboard_group_id,
                                                             dashboard_name=self.dashboard_id,
                                                             cluster=self.cluster,
                                                             product=self.product)

    def _get_dashboard_description_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_DESCRIPTION_FORMAT.format(dashboard_group=self.dashboard_group_id,
                                                                     dashboard_name=self.dashboard_id,
                                                                     cluster=self.cluster,
                                                                     product=self.product)

    def _get_dashboard_group_description_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_GROUP_DESCRIPTION_KEY_FORMAT.format(dashboard_group=self.dashboard_group_id,
                                                                               cluster=self.cluster,
                                                                               product=self.product)

    def _get_dashboard_group_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_GROUP_KEY_FORMAT.format(dashboard_group=self.dashboard_group_id,
                                                                   cluster=self.cluster,
                                                                   product=self.product)

    def _get_dashboard_last_reload_time_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME_FORMAT.format(dashboard_group=self.dashboard_group,
                                                                          dashboard_name=self.dashboard_id,
                                                                          cluster=self.cluster,
                                                                          product=self.product)

    def create_next_node(self):
        # type: () -> Union[Dict[str, Any], None]
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_next_node(self):
        # type: () -> Iterator[Any]
        # Cluster node
        if not self._get_cluster_key() in self._processed_cluster:
            self._processed_cluster.add(self._get_cluster_key())
            yield {
                NODE_LABEL: cluster_constants.CLUSTER_NODE_LABEL,
                NODE_KEY: self._get_cluster_key(),
                cluster_constants.CLUSTER_NAME_PROP_KEY: self.cluster
            }

        # Dashboard node
        dashboard_node = {
            NODE_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
            NODE_KEY: self._get_dashboard_key(),
            DashboardMetadata.DASHBOARD_NAME: self.dashboard_name,
        }
        if self.created_timestamp:
            dashboard_node[DashboardMetadata.DASHBOARD_CREATED_TIME_STAMP] = self.created_timestamp

        if self.dashboard_url:
            dashboard_node[DashboardMetadata.DASHBOARD_URL] = self.dashboard_url

        yield dashboard_node

        # Dashboard group
        if self.dashboard_group and not self._get_dashboard_group_key() in self._processed_dashboard_group:
            self._processed_dashboard_group.add(self._get_dashboard_group_key())
            dashboard_group_node = {
                NODE_LABEL: DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
                NODE_KEY: self._get_dashboard_group_key(),
                DashboardMetadata.DASHBOARD_NAME: self.dashboard_group,
            }

            if self.dashboard_group_url:
                dashboard_group_node[DashboardMetadata.DASHBOARD_GROUP_URL] = self.dashboard_group_url

            yield dashboard_group_node

        # Dashboard group description
        if self.dashboard_group_description:
            yield {NODE_LABEL: DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                   NODE_KEY: self._get_dashboard_group_description_key(),
                   DashboardMetadata.DASHBOARD_DESCRIPTION: self.dashboard_group_description}

        # Dashboard description node
        if self.description:
            yield {NODE_LABEL: DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                   NODE_KEY: self._get_dashboard_description_key(),
                   DashboardMetadata.DASHBOARD_DESCRIPTION: self.description}

        # Dashboard tag node
        if self.tags:
            for tag in self.tags:
                yield {NODE_LABEL: TagMetadata.TAG_NODE_LABEL,
                       NODE_KEY: TagMetadata.get_tag_key(tag),
                       TagMetadata.TAG_TYPE: 'dashboard'}

    def create_next_relation(self):
        # type: () -> Union[Dict[str, Any], None]
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_next_relation(self):
        # type: () -> Iterator[Any]

        # Cluster <-> Dashboard group
        yield {
            RELATION_START_LABEL: cluster_constants.CLUSTER_NODE_LABEL,
            RELATION_END_LABEL: DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
            RELATION_START_KEY: self._get_cluster_key(),
            RELATION_END_KEY: self._get_dashboard_group_key(),
            RELATION_TYPE: DashboardMetadata.CLUSTER_DASHBOARD_GROUP_RELATION_TYPE,
            RELATION_REVERSE_TYPE: DashboardMetadata.DASHBOARD_GROUP_CLUSTER_RELATION_TYPE
        }

        # Dashboard group > Dashboard group description relation
        if self.dashboard_group_description:
            yield {
                RELATION_START_LABEL: DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
                RELATION_END_LABEL: DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                RELATION_START_KEY: self._get_dashboard_group_key(),
                RELATION_END_KEY: self._get_dashboard_group_description_key(),
                RELATION_TYPE: DashboardMetadata.DASHBOARD_DESCRIPTION_RELATION_TYPE,
                RELATION_REVERSE_TYPE: DashboardMetadata.DESCRIPTION_DASHBOARD_RELATION_TYPE
            }

        # Dashboard group > Dashboard relation
        yield {
            RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
            RELATION_END_LABEL: DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
            RELATION_START_KEY: self._get_dashboard_key(),
            RELATION_END_KEY: self._get_dashboard_group_key(),
            RELATION_TYPE: DashboardMetadata.DASHBOARD_DASHBOARD_GROUP_RELATION_TYPE,
            RELATION_REVERSE_TYPE: DashboardMetadata.DASHBOARD_GROUP_DASHBOARD_RELATION_TYPE
        }

        # Dashboard > Dashboard description relation
        if self.description:
            yield {
                RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                RELATION_END_LABEL: DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                RELATION_START_KEY: self._get_dashboard_key(),
                RELATION_END_KEY: self._get_dashboard_description_key(),
                RELATION_TYPE: DashboardMetadata.DASHBOARD_DESCRIPTION_RELATION_TYPE,
                RELATION_REVERSE_TYPE: DashboardMetadata.DESCRIPTION_DASHBOARD_RELATION_TYPE
            }

        # Dashboard > Dashboard tag relation
        if self.tags:
            for tag in self.tags:
                yield {
                    RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                    RELATION_END_LABEL: TagMetadata.TAG_NODE_LABEL,
                    RELATION_START_KEY: self._get_dashboard_key(),
                    RELATION_END_KEY: TagMetadata.get_tag_key(tag),
                    RELATION_TYPE: DashboardMetadata.DASHBOARD_TAG_RELATION_TYPE,
                    RELATION_REVERSE_TYPE: DashboardMetadata.TAG_DASHBOARD_RELATION_TYPE
                }
