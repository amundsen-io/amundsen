# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from typing import Optional, Dict, Any, Union, Iterator

from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, NODE_LABEL, NODE_KEY, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)

LOGGER = logging.getLogger(__name__)


class DashboardExecution(Neo4jCsvSerializable):
    """
    A model that encapsulate Dashboard's execution timestamp in epoch and execution state
    """
    DASHBOARD_EXECUTION_LABEL = 'Execution'
    DASHBOARD_EXECUTION_KEY_FORMAT = '{product}_dashboard://{cluster}.{dashboard_group_id}/' \
                                     '{dashboard_id}/execution/{execution_id}'
    DASHBOARD_EXECUTION_RELATION_TYPE = 'EXECUTED'
    EXECUTION_DASHBOARD_RELATION_TYPE = 'EXECUTION_OF'

    LAST_EXECUTION_ID = '_last_execution'
    LAST_SUCCESSFUL_EXECUTION_ID = '_last_successful_execution'

    def __init__(self,
                 dashboard_group_id: Optional[str],
                 dashboard_id: Optional[str],
                 execution_timestamp: int,
                 execution_state: str,
                 execution_id: str = LAST_EXECUTION_ID,
                 product: Optional[str] = '',
                 cluster: str = 'gold',
                 **kwargs: Any
                 ) -> None:
        self._dashboard_group_id = dashboard_group_id
        self._dashboard_id = dashboard_id
        self._execution_timestamp = execution_timestamp
        self._execution_state = execution_state
        self._execution_id = execution_id
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
            NODE_LABEL: DashboardExecution.DASHBOARD_EXECUTION_LABEL,
            NODE_KEY: self._get_last_execution_node_key(),
            'timestamp': self._execution_timestamp,
            'state': self._execution_state
        }

    def create_next_relation(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_relation_iterator(self) -> Iterator[Dict[str, Any]]:
        yield {
            RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
            RELATION_END_LABEL: DashboardExecution.DASHBOARD_EXECUTION_LABEL,
            RELATION_START_KEY: DashboardMetadata.DASHBOARD_KEY_FORMAT.format(
                product=self._product,
                cluster=self._cluster,
                dashboard_group=self._dashboard_group_id,
                dashboard_name=self._dashboard_id
            ),
            RELATION_END_KEY: self._get_last_execution_node_key(),
            RELATION_TYPE: DashboardExecution.DASHBOARD_EXECUTION_RELATION_TYPE,
            RELATION_REVERSE_TYPE: DashboardExecution.EXECUTION_DASHBOARD_RELATION_TYPE
        }

    def _get_last_execution_node_key(self) -> str:
        return DashboardExecution.DASHBOARD_EXECUTION_KEY_FORMAT.format(
            product=self._product,
            cluster=self._cluster,
            dashboard_group_id=self._dashboard_group_id,
            dashboard_id=self._dashboard_id,
            execution_id=self._execution_id
        )

    def __repr__(self) -> str:
        return 'DashboardExecution({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r})'.format(
            self._dashboard_group_id,
            self._dashboard_id,
            self._execution_timestamp,
            self._execution_state,
            self._execution_id,
            self._product,
            self._cluster
        )
