# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from typing import Optional, Dict, Any, Union, Iterator

from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, NODE_LABEL, NODE_KEY, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)
from databuilder.models.timestamp import timestamp_constants

LOGGER = logging.getLogger(__name__)


class DashboardLastModifiedTimestamp(Neo4jCsvSerializable):
    """
    A model that encapsulate Dashboard's last modified timestamp in epoch
    """

    DASHBOARD_LAST_MODIFIED_KEY_FORMAT = '{product}_dashboard://{cluster}.{dashboard_group_id}/' \
                                         '{dashboard_id}/_last_modified_timestamp'

    def __init__(self,
                 dashboard_group_id: Optional[str],
                 dashboard_id: Optional[str],
                 last_modified_timestamp: int,
                 product: Optional[str] = '',
                 cluster: str = 'gold',
                 **kwargs: Any
                 ) -> None:
        self._dashboard_group_id = dashboard_group_id
        self._dashboard_id = dashboard_id
        self._last_modified_timestamp = last_modified_timestamp
        self._product = product
        self._cluster = cluster
        self._node_iterator = self._create_node_iterator()
        self._relation_iterator = self._create_relation_iterator()

    def create_next_node(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[Dict[str, Any]]:  # noqa: C901
        yield {
            NODE_LABEL: timestamp_constants.NODE_LABEL,
            NODE_KEY: self._get_last_modified_node_key(),
            timestamp_constants.TIMESTAMP_PROPERTY: self._last_modified_timestamp,
            timestamp_constants.TIMESTAMP_NAME_PROPERTY: timestamp_constants.TimestampName.last_updated_timestamp.name,
        }

    def create_next_relation(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_relation_iterator(self) -> Iterator[Dict[str, Any]]:
        yield {
            RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
            RELATION_END_LABEL: timestamp_constants.NODE_LABEL,
            RELATION_START_KEY: DashboardMetadata.DASHBOARD_KEY_FORMAT.format(
                product=self._product,
                cluster=self._cluster,
                dashboard_group=self._dashboard_group_id,
                dashboard_name=self._dashboard_id
            ),
            RELATION_END_KEY: self._get_last_modified_node_key(),
            RELATION_TYPE: timestamp_constants.LASTUPDATED_RELATION_TYPE,
            RELATION_REVERSE_TYPE: timestamp_constants.LASTUPDATED_REVERSE_RELATION_TYPE
        }

    def _get_last_modified_node_key(self) -> str:
        return DashboardLastModifiedTimestamp.DASHBOARD_LAST_MODIFIED_KEY_FORMAT.format(
            product=self._product,
            cluster=self._cluster,
            dashboard_group_id=self._dashboard_group_id,
            dashboard_id=self._dashboard_id,
        )

    def __repr__(self) -> str:
        return 'DashboardLastModifiedTimestamp({!r}, {!r}, {!r}, {!r}, {!r})'.format(
            self._dashboard_group_id,
            self._dashboard_id,
            self._last_modified_timestamp,
            self._product,
            self._cluster
        )
