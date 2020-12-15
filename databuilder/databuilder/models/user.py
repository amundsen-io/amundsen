# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import copy
from typing import (
    Any, List, Optional,
)

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable


class User(GraphSerializable):
    """
    User model. This model doesn't define any relationship.
    """
    USER_NODE_LABEL = 'User'
    USER_NODE_KEY_FORMAT = '{email}'
    USER_NODE_EMAIL = 'email'
    USER_NODE_FIRST_NAME = 'first_name'
    USER_NODE_LAST_NAME = 'last_name'
    USER_NODE_FULL_NAME = 'full_name'
    USER_NODE_GITHUB_NAME = 'github_username'
    USER_NODE_TEAM = 'team_name'
    USER_NODE_EMPLOYEE_TYPE = 'employee_type'
    USER_NODE_MANAGER_EMAIL = 'manager_email'
    USER_NODE_SLACK_ID = 'slack_id'
    USER_NODE_IS_ACTIVE = 'is_active'  # bool value needs to be unquoted when publish to neo4j
    USER_NODE_UPDATED_AT = 'updated_at'
    USER_NODE_ROLE_NAME = 'role_name'

    USER_MANAGER_RELATION_TYPE = 'MANAGE_BY'
    MANAGER_USER_RELATION_TYPE = 'MANAGE'

    def __init__(self,
                 email: str,
                 first_name: str = '',
                 last_name: str = '',
                 name: str = '',
                 github_username: str = '',
                 team_name: str = '',
                 employee_type: str = '',
                 manager_email: str = '',
                 slack_id: str = '',
                 is_active: bool = True,
                 updated_at: int = 0,
                 role_name: str = '',
                 do_not_update_empty_attribute: bool = False,
                 **kwargs: Any
                 ) -> None:
        """
        This class models user node for Amundsen people.

        :param first_name:
        :param last_name:
        :param name:
        :param email:
        :param github_username:
        :param team_name:
        :param employee_type:
        :param manager_email:
        :param is_active:
        :param updated_at: everytime we update the node, we will push the timestamp.
                           then we will have a cron job to update the ex-employee nodes based on
                           the case if this timestamp hasn't been updated for two weeks.
        :param role_name: the role_name of the user (e.g swe)
        :param do_not_update_empty_attribute: If False, all empty or not defined params will be overwritten with
        empty string.
        :param kwargs: Any K/V attributes we want to update the
        """
        self.first_name = first_name
        self.last_name = last_name
        self.name = name

        self.email = email
        self.github_username = github_username
        # todo: team will be a separate node once Amundsen People supports team
        self.team_name = team_name
        self.manager_email = manager_email
        self.employee_type = employee_type
        # this attr not available in team service, either update team service, update with FE
        self.slack_id = slack_id
        self.is_active = is_active
        self.updated_at = updated_at
        self.role_name = role_name
        self.do_not_update_empty_attribute = do_not_update_empty_attribute
        self.attrs = None
        if kwargs:
            self.attrs = copy.deepcopy(kwargs)

        self._node_iter = iter(self.create_nodes())
        self._rel_iter = iter(self.create_relation())

    def create_next_node(self) -> Optional[GraphNode]:
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        """
        :return:
        """
        try:
            return next(self._rel_iter)
        except StopIteration:
            return None

    @classmethod
    def get_user_model_key(cls,
                           email: str = None
                           ) -> str:
        if not email:
            return ''
        return User.USER_NODE_KEY_FORMAT.format(email=email)

    def create_nodes(self) -> List[GraphNode]:
        """
        Create a list of Neo4j node records
        :return:
        """

        node_attributes = {
            User.USER_NODE_EMAIL: self.email,
            User.USER_NODE_IS_ACTIVE: self.is_active,
            User.USER_NODE_FIRST_NAME: self.first_name or '',
            User.USER_NODE_LAST_NAME: self.last_name or '',
            User.USER_NODE_FULL_NAME: self.name or '',
            User.USER_NODE_GITHUB_NAME: self.github_username or '',
            User.USER_NODE_TEAM: self.team_name or '',
            User.USER_NODE_EMPLOYEE_TYPE: self.employee_type or '',
            User.USER_NODE_SLACK_ID: self.slack_id or '',
            User.USER_NODE_ROLE_NAME: self.role_name or ''
        }

        if self.updated_at:
            node_attributes[User.USER_NODE_UPDATED_AT] = self.updated_at
        elif not self.do_not_update_empty_attribute:
            node_attributes[User.USER_NODE_UPDATED_AT] = 0

        if self.attrs:
            for k, v in self.attrs.items():
                if k not in node_attributes:
                    node_attributes[k] = v

        if self.do_not_update_empty_attribute:
            for k, v in list(node_attributes.items()):
                if not v:
                    del node_attributes[k]

        node = GraphNode(
            key=User.get_user_model_key(email=self.email),
            label=User.USER_NODE_LABEL,
            attributes=node_attributes
        )

        return [node]

    def create_relation(self) -> List[GraphRelationship]:
        if self.manager_email:
            # only create the relation if the manager exists
            relationship = GraphRelationship(
                start_key=User.get_user_model_key(email=self.email),
                start_label=User.USER_NODE_LABEL,
                end_label=User.USER_NODE_LABEL,
                end_key=self.get_user_model_key(email=self.manager_email),
                type=User.USER_MANAGER_RELATION_TYPE,
                reverse_type=User.MANAGER_USER_RELATION_TYPE,
                attributes={}
            )
            return [relationship]
        return []

    def __repr__(self) -> str:
        return f'User({self.first_name!r}, {self.last_name!r}, {self.name!r}, {self.email!r}, ' \
               f'{self.github_username!r}, {self.team_name!r}, {self.slack_id!r}, {self.manager_email!r}, ' \
               f'{self.employee_type!r}, {self.is_active!r}, {self.updated_at!r}, {self.role_name!r})'
