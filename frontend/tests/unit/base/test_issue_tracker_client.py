# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
import flask

from amundsen_application.base.base_issue_tracker_client import BaseIssueTrackerClient

app = flask.Flask(__name__)
app.config.from_object('amundsen_application.config.TestConfig')


class IssueTrackerClientTest(unittest.TestCase):
    def setUp(self) -> None:
        BaseIssueTrackerClient.__abstractmethods__ = frozenset()
        self.client = BaseIssueTrackerClient()

    def tearDown(self) -> None:
        pass

    def test_cover_get_issues(self) -> None:
        with app.test_request_context():
            try:
                self.client.get_issues(table_uri='test')
            except NotImplementedError:
                self.assertTrue(True)
            else:
                self.assertTrue(False)

    def test_cover_create_issue(self) -> None:
        with app.test_request_context():
            try:
                self.client.create_issue(table_uri='test', title='title', description='description')
            except NotImplementedError:
                self.assertTrue(True)
            else:
                self.assertTrue(False)
