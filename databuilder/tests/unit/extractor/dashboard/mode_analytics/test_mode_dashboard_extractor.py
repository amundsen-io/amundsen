# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from mock import patch
from pyhocon import ConfigFactory

from databuilder import Scoped
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_extractor import ModeDashboardExtractor
from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata


class TestModeDashboardExtractor(unittest.TestCase):
    def setUp(self) -> None:
        config = ConfigFactory.from_dict({
            'extractor.mode_dashboard.organization': 'amundsen',
            'extractor.mode_dashboard.mode_bearer_token': 'amundsen_bearer_token',
        })
        self.config = config

    def test_extractor_extract_record(self) -> None:
        extractor = ModeDashboardExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=self.config, scope=extractor.get_scope()))

        with patch('databuilder.rest_api.rest_api_query.RestApiQuery._send_request') as mock_request, \
                patch('databuilder.rest_api.query_merger.QueryMerger._compute_query_result') as mock_query_result:
            mock_request.return_value.json.return_value = {
                'reports': [
                    {
                        'token': 'ddd',
                        'name': 'dashboard name',
                        'description': 'dashboard description',
                        'created_at': '2021-02-05T21:20:09.019Z',
                        'space_token': 'ggg',
                    }
                ]
            }
            mock_query_result.return_value = {
                'ggg': {
                    'dashboard_group_id': 'ggg',
                    'dashboard_group': 'dashboard group name',
                    'dashboard_group_description': 'dashboard group description',
                }
            }

            record = next(extractor.extract())
            self.assertIsInstance(record, DashboardMetadata)
            self.assertEqual(record.dashboard_group, 'dashboard group name')
            self.assertEqual(record.dashboard_name, 'dashboard name')
            self.assertEqual(record.description, 'dashboard description')
            self.assertEqual(record.cluster, 'gold')
            self.assertEqual(record.product, 'mode')
            self.assertEqual(record.dashboard_group_id, 'ggg')
            self.assertEqual(record.dashboard_id, 'ddd')
            self.assertEqual(record.dashboard_group_description, 'dashboard group description')
            self.assertEqual(record.created_timestamp, 1612560009)
            self.assertEqual(record.dashboard_group_url, 'https://app.mode.com/amundsen/spaces/ggg')
            self.assertEqual(record.dashboard_url, 'https://app.mode.com/amundsen/reports/ddd')


if __name__ == '__main__':
    unittest.main()
