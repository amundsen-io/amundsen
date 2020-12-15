# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import (
    Any, Iterator, Optional, Union,
)

from databuilder.models.dashboard.dashboard_query import DashboardQuery
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable

LOGGER = logging.getLogger(__name__)


class DashboardChart(GraphSerializable):
    """
    A model that encapsulate Dashboard's charts
    """
    DASHBOARD_CHART_LABEL = 'Chart'
    DASHBOARD_CHART_KEY_FORMAT = '{product}_dashboard://{cluster}.{dashboard_group_id}/' \
                                 '{dashboard_id}/query/{query_id}/chart/{chart_id}'
    CHART_RELATION_TYPE = 'HAS_CHART'
    CHART_REVERSE_RELATION_TYPE = 'CHART_OF'

    def __init__(self,
                 dashboard_group_id: Optional[str],
                 dashboard_id: Optional[str],
                 query_id: str,
                 chart_id: str,
                 chart_name: Optional[str] = None,
                 chart_type: Optional[str] = None,
                 chart_url: Optional[str] = None,
                 product: Optional[str] = '',
                 cluster: str = 'gold',
                 **kwargs: Any
                 ) -> None:
        self._dashboard_group_id = dashboard_group_id
        self._dashboard_id = dashboard_id
        self._query_id = query_id
        self._chart_id = chart_id if chart_id else chart_name
        self._chart_name = chart_name
        self._chart_type = chart_type
        self._chart_url = chart_url
        self._product = product
        self._cluster = cluster
        self._node_iterator = self._create_node_iterator()
        self._relation_iterator = self._create_relation_iterator()

    def create_next_node(self) -> Union[GraphNode, None]:
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        node_attributes = {
            'id': self._chart_id
        }

        if self._chart_name:
            node_attributes['name'] = self._chart_name

        if self._chart_type:
            node_attributes['type'] = self._chart_type

        if self._chart_url:
            node_attributes['url'] = self._chart_url

        node = GraphNode(
            key=self._get_chart_node_key(),
            label=DashboardChart.DASHBOARD_CHART_LABEL,
            attributes=node_attributes
        )
        yield node

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        relationship = GraphRelationship(
            start_label=DashboardQuery.DASHBOARD_QUERY_LABEL,
            start_key=DashboardQuery.DASHBOARD_QUERY_KEY_FORMAT.format(
                product=self._product,
                cluster=self._cluster,
                dashboard_group_id=self._dashboard_group_id,
                dashboard_id=self._dashboard_id,
                query_id=self._query_id
            ),
            end_label=DashboardChart.DASHBOARD_CHART_LABEL,
            end_key=self._get_chart_node_key(),
            type=DashboardChart.CHART_RELATION_TYPE,
            reverse_type=DashboardChart.CHART_REVERSE_RELATION_TYPE,
            attributes={}
        )
        yield relationship

    def _get_chart_node_key(self) -> str:
        return DashboardChart.DASHBOARD_CHART_KEY_FORMAT.format(
            product=self._product,
            cluster=self._cluster,
            dashboard_group_id=self._dashboard_group_id,
            dashboard_id=self._dashboard_id,
            query_id=self._query_id,
            chart_id=self._chart_id
        )

    def __repr__(self) -> str:
        return f'DashboardChart({self._dashboard_group_id!r}, {self._dashboard_id!r}, ' \
               f'{self._query_id!r}, {self._chart_id!r}, {self._chart_name!r}, {self._chart_type!r}, ' \
               f'{self._chart_url!r}, {self._product!r}, {self._cluster!r})'
