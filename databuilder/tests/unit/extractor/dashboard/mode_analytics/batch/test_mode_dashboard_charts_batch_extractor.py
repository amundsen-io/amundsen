# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from mock import patch
from pyhocon import ConfigFactory

from databuilder import Scoped
from databuilder.extractor.dashboard.mode_analytics.batch.mode_dashboard_charts_batch_extractor import (
    ModeDashboardChartsBatchExtractor,
)


class TestModeDashboardChartsBatchExtractor(unittest.TestCase):
    def setUp(self) -> None:
        config = ConfigFactory.from_dict({
            'extractor.mode_dashboard_chart_batch.organization': 'amundsen',
            'extractor.mode_dashboard_chart_batch.mode_user_token': 'amundsen_user_token',
            'extractor.mode_dashboard_chart_batch.mode_password_token': 'amundsen_password_token',
            'extractor.mode_dashboard_chart_batch.mode_bearer_token': 'amundsen_bearer_token',
        })
        self.config = config

    def test_dashboard_chart_extractor_empty_record(self) -> None:
        extractor = ModeDashboardChartsBatchExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=self.config, scope=extractor.get_scope()))

        with patch('databuilder.rest_api.rest_api_query.requests.get'):
            record = extractor.extract()
            self.assertIsNone(record)

    def test_dashboard_chart_extractor_actual_record(self) -> None:
        extractor = ModeDashboardChartsBatchExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=self.config, scope=extractor.get_scope()))

        with patch('databuilder.extractor.restapi.rest_api_extractor.RestAPIExtractor.extract') as mock_get:
            mock_get.return_value = {
                'organization': 'amundsen',
                'is_active': None,
                'updated_at': None,
                'do_not_update_empty_attribute': True,
                'dashboard_group_id': 'ggg',
                'dashboard_id': 'ddd',
                'query_id': 'yyy',
                'chart_id': 'xxx',
                'chart_name': 'some chart',
                'chart_type': 'bigNumber',
                'product': 'mode'
            }

            record = extractor.extract()
            self.assertEqual(record._dashboard_group_id, 'ggg')
            self.assertEqual(record._dashboard_id, 'ddd')
            self.assertEqual(record._chart_name, 'some chart')
            self.assertEqual(record._product, 'mode')


if __name__ == '__main__':
    unittest.main()
