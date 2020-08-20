# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import re

from typing import Optional, Dict, Any, List, Union, Iterator

from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)
from databuilder.models.table_metadata import TableMetadata


LOGGER = logging.getLogger(__name__)


class DashboardTable(Neo4jCsvSerializable):
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

    def create_next_node(self) -> Union[Dict[str, Any], None]:
        return None

    def create_next_relation(self) -> Union[Dict[str, Any], None]:
        if self._relation_iterator is None:
            return None

        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_relation_iterator(self) -> Optional[Iterator[Dict[str, Any]]]:
        for table_id in self._table_ids:
            m = re.match('([^./]+)://([^./]+)\.([^./]+)\/([^./]+)', table_id)
            if m:
                yield {
                    RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                    RELATION_END_LABEL: TableMetadata.TABLE_NODE_LABEL,
                    RELATION_START_KEY: DashboardMetadata.DASHBOARD_KEY_FORMAT.format(
                        product=self._product,
                        cluster=self._cluster,
                        dashboard_group=self._dashboard_group_id,
                        dashboard_name=self._dashboard_id
                    ),
                    RELATION_END_KEY: TableMetadata.TABLE_KEY_FORMAT.format(
                        db=m.group(1),
                        cluster=m.group(2),
                        schema=m.group(3),
                        tbl=m.group(4)
                    ),
                    RELATION_TYPE: DashboardTable.DASHBOARD_TABLE_RELATION_TYPE,
                    RELATION_REVERSE_TYPE: DashboardTable.TABLE_DASHBOARD_RELATION_TYPE
                }

    def __repr__(self) -> str:
        return 'DashboardTable({!r}, {!r}, {!r}, {!r}, ({!r}))'.format(
            self._dashboard_group_id,
            self._dashboard_id,
            self._product,
            self._cluster,
            ','.join(self._table_ids),
        )
