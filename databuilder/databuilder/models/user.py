from typing import Union, Dict, Any  # noqa: F401

from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable, NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE


class User(Neo4jCsvSerializable):
    # type: (...) -> None
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
    USER_NODE_IS_ACTIVE = 'is_active'
    USER_NODE_UPDATED_AT = 'updated_at'

    USER_MANAGER_RELATION_TYPE = 'MANAGE_BY'
    MANAGER_USER_RELATION_TYPE = 'MANAGE'

    def __init__(self,
                 email,  # type: str
                 first_name='',  # type: str
                 last_name='',  # type: str
                 name='',  # type: str
                 github_username='',  # type: str
                 team_name='',  # type: str
                 employee_type='',  # type: str
                 manager_email='',  # type: str
                 slack_id='',  # type: str
                 is_active=True,  # type: bool
                 updated_at=0,  # type: int
                 ):
        # type: (...) -> None
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
        """
        self.first_name = first_name.encode('utf-8')
        self.last_name = last_name.encode('utf-8')
        self.name = name.encode('utf-8')

        self.email = email.encode('utf-8')
        self.github_username = github_username.encode('utf-8')
        # todo: team will be a separate node once Amundsen People supports team
        self.team_name = team_name.encode('utf-8')
        self.manager_email = manager_email.encode('utf-8')
        self.employee_type = employee_type.encode('utf-8')
        # this attr not available in team service, either update team service, update with FE
        self.slack_id = slack_id.encode('utf-8')
        self.is_active = is_active
        self.updated_at = updated_at

        self._node_iter = iter(self.create_nodes())
        self._rel_iter = iter(self.create_relation())

    def create_next_node(self):
        # type: (...) -> Union[Dict[str, Any], None]
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self):
        # type: () -> Union[Dict[str, Any], None]
        """
        :return:
        """
        try:
            return next(self._rel_iter)
        except StopIteration:
            return None

    @classmethod
    def get_user_model_key(cls,
                           email=None):
        # type: (...) -> str
        if not email:
            return ''
        return User.USER_NODE_KEY_FORMAT.format(email=email)

    def create_nodes(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of Neo4j node records
        :return:
        """
        result_node = {
            NODE_KEY: User.get_user_model_key(email=self.email),
            NODE_LABEL: User.USER_NODE_LABEL,
            User.USER_NODE_EMAIL: self.email,
            User.USER_NODE_IS_ACTIVE: self.is_active,
        }

        result_node[User.USER_NODE_FIRST_NAME] = self.first_name if self.first_name else ''
        result_node[User.USER_NODE_LAST_NAME] = self.last_name if self.last_name else ''
        result_node[User.USER_NODE_FULL_NAME] = self.name if self.name else ''
        result_node[User.USER_NODE_GITHUB_NAME] = self.github_username if self.github_username else ''
        result_node[User.USER_NODE_TEAM] = self.team_name if self.team_name else ''
        result_node[User.USER_NODE_EMPLOYEE_TYPE] = self.employee_type if self.employee_type else ''
        result_node[User.USER_NODE_SLACK_ID] = self.slack_id if self.slack_id else ''
        result_node[User.USER_NODE_UPDATED_AT] = self.updated_at if self.updated_at else 0

        return [result_node]

    def create_relation(self):
        # type: () -> List[Dict[str, Any]]
        if self.manager_email:
            # only create the relation if the manager exists
            return [{
                RELATION_START_KEY: User.get_user_model_key(email=self.email),
                RELATION_START_LABEL: User.USER_NODE_LABEL,
                RELATION_END_KEY: self.get_user_model_key(email=self.manager_email),
                RELATION_END_LABEL: User.USER_NODE_LABEL,
                RELATION_TYPE: User.USER_MANAGER_RELATION_TYPE,
                RELATION_REVERSE_TYPE: User.MANAGER_USER_RELATION_TYPE
            }]
        return []

    def __repr__(self):
        # type: () -> str
        return 'User({!r}, {!r}, {!r}, {!r}, {!r}, ' \
               '{!r}, {!r}, {!r}, {!r}, {!r}, {!r},)'.format(self.first_name,
                                                             self.last_name,
                                                             self.name,
                                                             self.email,
                                                             self.github_username,
                                                             self.team_name,
                                                             self.slack_id,
                                                             self.manager_email,
                                                             self.employee_type,
                                                             self.is_active)
