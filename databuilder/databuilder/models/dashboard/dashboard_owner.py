# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import (
    Any, Iterator, Optional, Union,
)

from amundsen_rds.models import RDSModel
from amundsen_rds.models.dashboard import DashboardOwner as RDSDashboardOwner

from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.owner_constants import OWNER_OF_OBJECT_RELATION_TYPE, OWNER_RELATION_TYPE
from databuilder.models.table_serializable import TableSerializable
from databuilder.models.user import User

LOGGER = logging.getLogger(__name__)


class DashboardOwner(GraphSerializable, TableSerializable):
    """
    A model that encapsulate Dashboard's owner.
    Note that it does not create new user as it has insufficient information about user but it builds relation
    between User and Dashboard
    """

    DASHBOARD_EXECUTION_RELATION_TYPE = 'LAST_EXECUTED'
    EXECUTION_DASHBOARD_RELATION_TYPE = 'LAST_EXECUTION_OF'

    def __init__(self,
                 dashboard_group_id: str,
                 dashboard_id: str,
                 email: str,
                 product: Optional[str] = '',
                 cluster: str = 'gold',
                 **kwargs: Any
                 ) -> None:
        self._dashboard_group_id = dashboard_group_id
        self._dashboard_id = dashboard_id
        self._email = email
        self._product = product
        self._cluster = cluster

        self._relation_iterator = self._create_relation_iterator()
        self._record_iterator = self._create_record_iterator()

    def create_next_node(self) -> Union[GraphNode, None]:
        return None

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        relationship = GraphRelationship(
            start_label=DashboardMetadata.DASHBOARD_NODE_LABEL,
            end_label=User.USER_NODE_LABEL,
            start_key=DashboardMetadata.DASHBOARD_KEY_FORMAT.format(
                product=self._product,
                cluster=self._cluster,
                dashboard_group=self._dashboard_group_id,
                dashboard_name=self._dashboard_id
            ),
            end_key=User.get_user_model_key(email=self._email),
            type=OWNER_RELATION_TYPE,
            reverse_type=OWNER_OF_OBJECT_RELATION_TYPE,
            attributes={}
        )
        yield relationship

    def create_next_record(self) -> Union[RDSModel, None]:
        try:
            return next(self._record_iterator)
        except StopIteration:
            return None

    def _create_record_iterator(self) -> Iterator[RDSModel]:
        yield RDSDashboardOwner(
            user_rk=User.get_user_model_key(email=self._email),
            dashboard_rk=DashboardMetadata.DASHBOARD_KEY_FORMAT.format(
                product=self._product,
                cluster=self._cluster,
                dashboard_group=self._dashboard_group_id,
                dashboard_name=self._dashboard_id
            )
        )

    def __repr__(self) -> str:
        return f'DashboardOwner({self._dashboard_group_id!r}, {self._dashboard_id!r}, ' \
               f'{self._email!r}, {self._product!r}, {self._cluster!r})'
