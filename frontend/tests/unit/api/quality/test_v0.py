# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from amundsen_application.base.base_quality_client import BaseQualityClient
from amundsen_application.api.quality import v0
from amundsen_application import create_app
from flask import Response
from http import HTTPStatus
import unittest
import json

local_app = create_app("amundsen_application.config.TestConfig", "tests/templates")


class DummyQualityClient(BaseQualityClient):
    """
    Dummy concrete class that can be instantiated.
    """

    def get_table_quality_checks_summary(self, *, table_key: str) -> Response:
        pass

    def get_table_quality_checks(self, *, table_key: str) -> bytes:
        pass


quality_client_class_name = "tests.unit.api.quality.test_v0.DummyQualityClient"


class QualityTest(unittest.TestCase):
    def test_no_client_class(self) -> None:
        """
        Test that when no quality client configured, endpoint returns expected not-implemented response.
        """
        # Reset side effects of other tests to ensure results consistent regardless of execution order.
        v0.QUALITY_CLIENT_INSTANCE = None

        local_app.config["QUALITY_CLIENT"] = None

        with local_app.test_client() as test:
            response = test.get("/api/quality/v0/table/summary?key=some_table_key")
            self.assertEqual(response.status_code, HTTPStatus.NOT_IMPLEMENTED)
            self.assertEqual(
                response.json,
                {
                    "checks": {},
                    "msg": "A client for retrieving quality checks must be configured",
                },
            )

    @unittest.mock.patch(
        quality_client_class_name + ".get_table_quality_checks_summary"
    )
    def test_good_client_response(
        self, mock_get_table_quality_checks_summary: unittest.mock.Mock
    ) -> None:
        local_app.config["QUALITY_CLIENT"] = quality_client_class_name
        mock_response_json = json.dumps(
            {
                "checks": {
                    "num_checks_success": 0,
                    "num_checks_failed": 0,
                    "num_checks_total": 0,
                    "external_url": "external/url",
                    "last_run_timestamp": None,
                },
                "msg": "Success",
            }
        )
        mock_get_table_quality_checks_summary.return_value = Response(
            response=mock_response_json, status=HTTPStatus.OK
        )

        with local_app.test_client() as test:
            response = test.get("api/quality/v0/table/summary?key=some_table_key")
            self.assertEqual(response.status_code, HTTPStatus.OK)
