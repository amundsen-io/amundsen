import json
import unittest

from databuilder.models.dashboard_elasticsearch_document import DashboardESDocument


class TestDashboardElasticsearchDocument(unittest.TestCase):

    def test_to_json(self):
        # type: () -> None
        """
        Test string generated from to_json method
        """
        test_obj = DashboardESDocument(dashboard_group='test_dashboard_group',
                                       dashboard_name='test_dashboard_name',
                                       description='test_description',
                                       last_reload_time='test_last_reload_time',
                                       user_id='test_user_id',
                                       user_name='test_user_name',
                                       tags=['test'])

        expected_document_dict = {"dashboard_group": "test_dashboard_group",
                                  "dashboard_name": "test_dashboard_name",
                                  "description": "test_description",
                                  "last_reload_time": "test_last_reload_time",
                                  "user_id": "test_user_id",
                                  "user_name": "test_user_name",
                                  "tags": ["test"]
                                  }

        result = test_obj.to_json()
        results = result.split("\n")

        # verify two new line characters in result
        self.assertEqual(len(results), 2, "Result from to_json() function doesn't have a newline!")
        self.assertDictEqual(json.loads(results[0]), expected_document_dict)
