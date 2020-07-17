# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
import flask

from amundsen_application.base.base_preview_client import BasePreviewClient

app = flask.Flask(__name__)
app.config.from_object('amundsen_application.config.LocalConfig')


class PreviewClientTest(unittest.TestCase):
    def setUp(self) -> None:
        BasePreviewClient.__abstractmethods__ = frozenset()
        self.client = BasePreviewClient()

    def tearDown(self) -> None:
        pass

    def cover_abtract_methods(self) -> None:
        with app.test_request_context():
            try:
                self.client.get_preview_data()
            except NotImplementedError:
                self.assertTrue(True)
            else:
                self.assertTrue(False)
