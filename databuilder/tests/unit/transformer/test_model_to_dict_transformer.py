# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.user_elasticsearch_document import UserESDocument
from databuilder.transformer.model_to_dict import ModelToDictTransformer


class TestModelToDictTransformer(unittest.TestCase):

    def test_to_dict(self) -> None:
        """
        Test dictionary generated from ModelToDict transformer
        """
        test_obj = UserESDocument(email='test@email.com',
                                  first_name='test_firstname',
                                  last_name='test_lastname',
                                  full_name='full_name',
                                  github_username='github_user',
                                  team_name='team',
                                  employee_type='fte',
                                  manager_email='test_manager',
                                  slack_id='test_slack',
                                  role_name='role_name',
                                  is_active=True,
                                  total_read=2,
                                  total_own=3,
                                  total_follow=1)

        expected_document_dict = {"first_name": "test_firstname",
                                  "last_name": "test_lastname",
                                  "name": "full_name",
                                  "team_name": "team",
                                  "total_follow": 1,
                                  "total_read": 2,
                                  "is_active": True,
                                  "total_own": 3,
                                  "slack_id": 'test_slack',
                                  "role_name": 'role_name',
                                  "manager_email": "test_manager",
                                  'github_username': "github_user",
                                  "employee_type": 'fte',
                                  "key": "test@email.com",
                                  }

        transformer = ModelToDictTransformer()
        result = transformer.transform(test_obj)

        self.assertEqual(result, expected_document_dict)
