# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import unittest

from databuilder.models.metric_elasticsearch_document import MetricESDocument


class TestMetricElasticsearchDocument(unittest.TestCase):

    def test_to_json(self) -> None:
        """
        Test string generated from to_json method
        """

        test_obj = MetricESDocument(name='test_metric_name',
                                    description='test_metric_description',
                                    type='test_metric_type',
                                    dashboards=['test_dashboard_1', 'test_dashboard_2'],
                                    tags=['test_metric_group'])

        expected_document_dict = {"name": "test_metric_name",
                                  "description": "test_metric_description",
                                  "type": "test_metric_type",
                                  "dashboards": ['test_dashboard_1', 'test_dashboard_2'],
                                  "tags": ['test_metric_group']
                                  }

        result = test_obj.to_json()
        results = result.split("\n")

        # verify two new line characters in result
        self.assertEqual(len(results), 2, "Result from to_json() function doesn't have a newline!")
        self.assertDictEqual(json.loads(results[0]), expected_document_dict)
