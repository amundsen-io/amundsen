# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import re
from typing import (
    Any, Iterator, List, Optional, Union,
)

from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import TableMetadata

LOGGER = logging.getLogger(__name__)


class DashboardTable(GraphSerializable):
    """
    A model that link Dashboard with the tables used in various charts of the dashboard.
    Note that it does not create new dashboard, table as it has insufficient information but it builds relation
    between Tables and Dashboard
    """

    DASHBOARD_TABLE_RELATION_TYPE = 'DASHBOARD_WITH_TABLE'
    TABLE_DASHBOARD_RELATION_TYPE = 'TABLE_OF_DASHBOARD'

    def __init__(self,
                 dashboard_group_id: str,
                 dashboard_id: str,
                 table_ids: List[str],
                 product: Optional[str] = '',
                 cluster: str = 'gold',
                 **kwargs: Any
                 ) -> None:
        self._dashboard_group_id = dashboard_group_id
        self._dashboard_id = dashboard_id
        # A list of tables uri used in the dashboard
        self._table_ids = table_ids
        self._product = product
        self._cluster = cluster

        self._relation_iterator = self._create_relation_iterator()

    def create_next_node(self) -> Union[GraphNode, None]:
        return None

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        if self._relation_iterator is None:
            return None
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        for table_id in self._table_ids:
            m = re.match(r'([^./]+)://([^./]+)\.([^./]+)\/([^./]+)', table_id)
            if m:
                relationship = GraphRelationship(
                    start_label=DashboardMetadata.DASHBOARD_NODE_LABEL,
                    end_label=TableMetadata.TABLE_NODE_LABEL,
                    start_key=DashboardMetadata.DASHBOARD_KEY_FORMAT.format(
                        product=self._product,
                        cluster=self._cluster,
                        dashboard_group=self._dashboard_group_id,
                        dashboard_name=self._dashboard_id
                    ),
                    end_key=TableMetadata.TABLE_KEY_FORMAT.format(
                        db=m.group(1),
                        cluster=m.group(2),
                        schema=m.group(3),
                        tbl=m.group(4)
                    ),
                    type=DashboardTable.DASHBOARD_TABLE_RELATION_TYPE,
                    reverse_type=DashboardTable.TABLE_DASHBOARD_RELATION_TYPE,
                    attributes={}
                )
                yield relationship

    def __repr__(self) -> str:
        return f'DashboardTable({self._dashboard_group_id!r}, {self._dashboard_id!r}, ' \
               f'{self._product!r}, {self._cluster!r}, ({",".join(self._table_ids)!r}))'
