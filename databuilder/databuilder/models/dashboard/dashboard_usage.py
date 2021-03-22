# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import (
    Any, Iterator, Optional, Union,
)

from amundsen_rds.models import RDSModel
from amundsen_rds.models.dashboard import DashboardUsage as RDSDashboardUsage

from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_serializable import TableSerializable
from databuilder.models.usage.usage_constants import (
    READ_RELATION_COUNT_PROPERTY, READ_RELATION_TYPE, READ_REVERSE_RELATION_TYPE,
)
from databuilder.models.user import User

LOGGER = logging.getLogger(__name__)


class DashboardUsage(GraphSerializable, TableSerializable):
    """
    A model that encapsulate Dashboard usage between Dashboard and User
    """

    def __init__(self,
                 dashboard_group_id: Optional[str],
                 dashboard_id: Optional[str],
                 email: str,
                 view_count: int,
                 should_create_user_node: Optional[bool] = False,
                 product: Optional[str] = '',
                 cluster: Optional[str] = 'gold',
                 **kwargs: Any
                 ) -> None:
        """

        :param dashboard_group_id:
        :param dashboard_id:
        :param email:
        :param view_count:
        :param should_create_user_node: Enable this if it is fine to create/update User node with only with email
        address. Please be advised that other fields will be emptied. Current use case is to create anonymous user.
        For example, Mode dashboard does not provide which user viewed the dashboard and anonymous user can be used
        to show the usage.
        :param product:
        :param cluster:
        :param kwargs:
        """
        self._dashboard_group_id = dashboard_group_id
        self._dashboard_id = dashboard_id
        self._email = email
        self._view_count = int(view_count)
        self._product = product
        self._cluster = cluster
        self._user_model = User(email=email)
        self._should_create_user_node = bool(should_create_user_node)
        self._relation_iterator = self._create_relation_iterator()
        self._record_iterator = self._create_record_iterator()

    def create_next_node(self) -> Union[GraphNode, None]:
        if self._should_create_user_node:
            return self._user_model.create_next_node()

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
            type=READ_REVERSE_RELATION_TYPE,
            reverse_type=READ_RELATION_TYPE,
            attributes={
                READ_RELATION_COUNT_PROPERTY: self._view_count
            }
        )
        yield relationship

    def create_next_record(self) -> Union[RDSModel, None]:
        try:
            return next(self._record_iterator)
        except StopIteration:
            return None

    def _create_record_iterator(self) -> Iterator[RDSModel]:
        if self._should_create_user_node:
            user_record = self._user_model.create_next_record()
            if user_record:
                yield user_record

        dashboard_usage_record = RDSDashboardUsage(
            user_rk=User.get_user_model_key(email=self._email),
            dashboard_rk=DashboardMetadata.DASHBOARD_KEY_FORMAT.format(
                product=self._product,
                cluster=self._cluster,
                dashboard_group=self._dashboard_group_id,
                dashboard_name=self._dashboard_id
            ),
            read_count=self._view_count
        )
        yield dashboard_usage_record

    def __repr__(self) -> str:
        return f'DashboardUsage({self._dashboard_group_id!r}, {self._dashboard_id!r}, ' \
               f'{self._email!r}, {self._view_count!r}, {self._should_create_user_node!r}, ' \
               f'{self._product!r}, {self._cluster!r})'
