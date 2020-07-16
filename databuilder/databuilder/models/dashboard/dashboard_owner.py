# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from typing import Optional, Dict, Any, Union, Iterator  # noqa: F401

from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)
from databuilder.models.owner_constants import OWNER_OF_OBJECT_RELATION_TYPE, OWNER_RELATION_TYPE
from databuilder.models.user import User


LOGGER = logging.getLogger(__name__)


class DashboardOwner(Neo4jCsvSerializable):
    """
    A model that encapsulate Dashboard's owner.
    Note that it does not create new user as it has insufficient information about user but it builds relation
    between User and Dashboard
    """

    DASHBOARD_EXECUTION_RELATION_TYPE = 'LAST_EXECUTED'
    EXECUTION_DASHBOARD_RELATION_TYPE = 'LAST_EXECUTION_OF'

    def __init__(self,
                 dashboard_group_id,  # type: str
                 dashboard_id,  # type: str
                 email,  # type: str
                 product='',  # type: Optional[str]
                 cluster='gold',  # type: str
                 **kwargs
                 ):
        self._dashboard_group_id = dashboard_group_id
        self._dashboard_id = dashboard_id
        self._email = email
        self._product = product
        self._cluster = cluster

        self._relation_iterator = self._create_relation_iterator()

    def create_next_node(self):
        # type: () -> Union[Dict[str, Any], None]
        return None

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
            RELATION_TYPE: OWNER_RELATION_TYPE,
            RELATION_REVERSE_TYPE: OWNER_OF_OBJECT_RELATION_TYPE
        }

    def __repr__(self):
        return 'DashboardOwner({!r}, {!r}, {!r}, {!r}, {!r})'.format(
            self._dashboard_group_id,
            self._dashboard_id,
            self._email,
            self._product,
            self._cluster
        )
