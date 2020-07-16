# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from typing import Optional, Dict, Any, Union, Iterator  # noqa: F401

from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)
from databuilder.models.usage.usage_constants import (
    READ_RELATION_TYPE, READ_REVERSE_RELATION_TYPE, READ_RELATION_COUNT_PROPERTY
)
from databuilder.models.user import User

LOGGER = logging.getLogger(__name__)


class DashboardUsage(Neo4jCsvSerializable):
    """
    A model that encapsulate Dashboard usage between Dashboard and User
    """

    def __init__(self,
                 dashboard_group_id,  # type: Optional[str]
                 dashboard_id,  # type: Optional[str]
                 email,  # type: str
                 view_count,  # type: int
                 should_create_user_node=False,  # type: Optional[bool]
                 product='',  # type: Optional[str]
                 cluster='gold',  # type: Optional[str]
                 **kwargs
                 ):
        # type: () -> None
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
        self._view_count = view_count
        self._product = product
        self._cluster = cluster
        self._user_model = User(email=email)
        self._should_create_user_node = bool(should_create_user_node)
        self._relation_iterator = self._create_relation_iterator()

    def create_next_node(self):
        # type: () -> Union[Dict[str, Any], None]
        if self._should_create_user_node:
            return self._user_model.create_next_node()

    def create_next_relation(self):
        # type: () -> Union[Dict[str, Any], None]
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_relation_iterator(self):
        # type: () -> Iterator[[Dict[str, Any]]]

        yield {
            RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
            RELATION_END_LABEL: User.USER_NODE_LABEL,
            RELATION_START_KEY: DashboardMetadata.DASHBOARD_KEY_FORMAT.format(
                product=self._product,
                cluster=self._cluster,
                dashboard_group=self._dashboard_group_id,
                dashboard_name=self._dashboard_id
            ),
            RELATION_END_KEY: User.get_user_model_key(email=self._email),
            RELATION_TYPE: READ_REVERSE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: READ_RELATION_TYPE,
            READ_RELATION_COUNT_PROPERTY: self._view_count
        }

    def __repr__(self):
        return 'DashboardUsage({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r})'.format(
            self._dashboard_group_id,
            self._dashboard_id,
            self._email,
            self._view_count,
            self._should_create_user_node,
            self._product,
            self._cluster
        )
