# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Iterator,
    List,
    Optional,
    Union,
)

from amundsen_rds.models import RDSModel
from amundsen_rds.models.table import TableFollower as RDSTableFollower
from amundsen_rds.models.user import User as RDSUser

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.follower_constants import FOLLOWER_OF_OBJECT_RELATION_TYPE, FOLLOWER_RELATION_TYPE
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.table_serializable import TableSerializable
from databuilder.models.user import User


class Follower(GraphSerializable, TableSerializable):
    LABELS_PERMITTED_TO_HAVE_FOLLOWER = ['Table', 'Dashboard']

    def __init__(
        self,
        start_label: str,
        start_key: str,
        follower_emails: Union[List, str],
    ) -> None:
        if start_label not in Follower.LABELS_PERMITTED_TO_HAVE_FOLLOWER:
            raise Exception(f'followers for {start_label} are not supported')
        self.start_label = start_label
        self.start_key = start_key
        if isinstance(follower_emails, str):
            follower_emails = follower_emails.split(',')
        self.follower_emails = [
            email.strip().lower() for email in follower_emails
        ]

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()
        self._record_iter = self._create_record_iterator()

    def __repr__(self) -> str:
        return f'follower({self.start_label!r}, {self.start_key!r}, {self.follower_emails!r})'

    def create_next_node(self) -> Optional[GraphNode]:
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def create_next_record(self) -> Union[RDSModel, None]:
        try:
            return next(self._record_iter)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        for email in self.follower_emails:
            if email:
                yield GraphNode(key=User.get_user_model_key(email=email),
                                label=User.USER_NODE_LABEL,
                                attributes={
                                    User.USER_NODE_EMAIL: email,
                                })

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        for email in self.follower_emails:
            if email:
                yield GraphRelationship(
                    start_label=self.start_label,
                    start_key=self.start_key,
                    end_label=User.USER_NODE_LABEL,
                    end_key=User.get_user_model_key(email=email),
                    type=FOLLOWER_RELATION_TYPE,
                    reverse_type=FOLLOWER_OF_OBJECT_RELATION_TYPE,
                    attributes={})

    def _create_record_iterator(self) -> Iterator[RDSModel]:
        for email in self.follower_emails:
            if email:
                user_record = RDSUser(rk=User.get_user_model_key(email=email),
                                      email=email)
                yield user_record

                if self.start_label == TableMetadata.TABLE_NODE_LABEL:
                    yield RDSTableFollower(
                        table_rk=self.start_key,
                        user_rk=User.get_user_model_key(email=email),
                    )
                else:
                    raise Exception(
                        f'{self.start_label}<>follower relationship is not table serializable'
                    )
