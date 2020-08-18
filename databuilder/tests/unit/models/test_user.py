# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.neo4j_csv_serde import RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE
from databuilder.models.user import User


class TestUser(unittest.TestCase):

    def setUp(self) -> None:
        super(TestUser, self).setUp()
        self.user = User(first_name='test_first',
                         last_name='test_last',
                         name='test_first test_last',
                         email='test@email.com',
                         github_username='github_test',
                         team_name='test_team',
                         employee_type='FTE',
                         manager_email='test_manager@email.com',
                         slack_id='slack',
                         is_active=True,
                         updated_at=1,
                         role_name='swe')

    def test_get_user_model_key(self) -> None:
        user_email = User.get_user_model_key(email=self.user.email)
        self.assertEquals(user_email, '{email}'.format(email='test@email.com'))

    def test_create_nodes(self) -> None:
        nodes = self.user.create_nodes()
        self.assertEquals(len(nodes), 1)

    def test_create_node_additional_attr(self) -> None:
        test_user = User(first_name='test_first',
                         last_name='test_last',
                         name='test_first test_last',
                         email='test@email.com',
                         github_username='github_test',
                         team_name='test_team',
                         employee_type='FTE',
                         manager_email='test_manager@email.com',
                         slack_id='slack',
                         is_active=True,
                         updated_at=1,
                         role_name='swe',
                         enable_notify=True)
        nodes = test_user.create_nodes()
        self.assertEqual(nodes[0]['email'], 'test@email.com')
        self.assertEqual(nodes[0]['role_name'], 'swe')
        self.assertTrue(nodes[0]['enable_notify'])

    def test_create_relation(self) -> None:
        relations = self.user.create_relation()
        self.assertEquals(len(relations), 1)

        start_key = '{email}'.format(email='test@email.com')
        end_key = '{email}'.format(email='test_manager@email.com')

        relation = {
            RELATION_START_KEY: start_key,
            RELATION_START_LABEL: User.USER_NODE_LABEL,
            RELATION_END_KEY: end_key,
            RELATION_END_LABEL: User.USER_NODE_LABEL,
            RELATION_TYPE: User.USER_MANAGER_RELATION_TYPE,
            RELATION_REVERSE_TYPE: User.MANAGER_USER_RELATION_TYPE
        }

        self.assertTrue(relation in relations)

    def test_not_including_empty_attribute(self) -> None:
        test_user = User(email='test@email.com',
                         foo='bar')

        self.assertDictEqual(test_user.create_next_node() or {},
                             {'KEY': 'test@email.com', 'LABEL': 'User', 'email': 'test@email.com',
                              'is_active:UNQUOTED': True, 'first_name': '', 'last_name': '', 'full_name': '',
                              'github_username': '', 'team_name': '', 'employee_type': '', 'slack_id': '',
                              'role_name': '', 'updated_at': 0, 'foo': 'bar'})

        test_user2 = User(email='test@email.com',
                          foo='bar',
                          is_active=False,
                          do_not_update_empty_attribute=True)

        self.assertDictEqual(test_user2.create_next_node() or {},
                             {'KEY': 'test@email.com', 'LABEL': 'User', 'email': 'test@email.com', 'foo': 'bar'})
