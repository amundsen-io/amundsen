# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from mock import patch
from pyhocon import ConfigFactory

from databuilder import Scoped
from databuilder.extractor.dashboard.mode_analytics.mode_dashboard_last_successful_executions_extractor import (
    ModeDashboardLastSuccessfulExecutionExtractor,
)
from databuilder.models.dashboard.dashboard_execution import DashboardExecution


class TestModeDashboardLastModifiedTimestampExtractor(unittest.TestCase):
    def setUp(self) -> None:
        config = ConfigFactory.from_dict({
            'extractor.mode_dashboard_last_successful_execution.organization': 'amundsen',
            'extractor.mode_dashboard_last_successful_execution.mode_bearer_token': 'amundsen_bearer_token',
        })
        self.config = config

    def test_extractor_extract_record(self) -> None:
        extractor = ModeDashboardLastSuccessfulExecutionExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=self.config, scope=extractor.get_scope()))

        with patch(
                'databuilder.rest_api.mode_analytics.mode_paginated_rest_api_query.ModePaginatedRestApiQuery.execute'
        ) as mock_execute:
            mock_execute.return_value = iter([
                {
                    'dashboard_group_id': 'ggg',
                    'dashboard_id': 'ddd',
                    'execution_timestamp': '2021-02-05T21:20:09.019Z',
                }
            ])

            record = next(extractor.extract())
            self.assertIsInstance(record, DashboardExecution)
            self.assertEqual(record._dashboard_group_id, 'ggg')
            self.assertEqual(record._dashboard_id, 'ddd')
            self.assertEqual(record._execution_timestamp, 1612560009)
            self.assertEqual(record._execution_state, 'succeeded')
            self.assertEqual(record._product, 'mode')
            self.assertEqual(record._cluster, 'gold')
            self.assertEqual(record._execution_id, '_last_successful_execution')


if __name__ == '__main__':
    unittest.main()
