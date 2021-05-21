# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from flask import current_app

from metadata_service import create_app


class BasicTestCase(unittest.TestCase):
    """
    Test the service if it can standup
    """

    def setUp(self) -> None:
        self.app = create_app(
            config_module_class='metadata_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self) -> None:
        self.app_context.pop()

    def test_no_hooks_called(self) -> None:
        with self.app.test_client() as c:
            resp = c.get('/some-endpoint')
            resp = self.app.process_response(resp)
            self.assertEqual(resp.headers.get('test_header'), None)

    def test_app_exists(self) -> None:
        self.assertFalse(current_app is None)


class TestConfigWithHooks(unittest.TestCase):
    """
    Test the service if it can standup
    """

    def setUp(self) -> None:
        self.app = create_app(
            config_module_class='metadata_service.tests.test_utils.TestHookConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self) -> None:
        self.app_context.pop()

    def test_hooks_called_once(self) -> None:
        with self.app.test_client() as c:
            resp = c.get('/some-endpoint')
            resp = self.app.process_response(resp)
            self.assertEqual(resp.headers.get('test_header'), '123')
