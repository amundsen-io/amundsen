# flake8: noqa
import unittest
from unittest.mock import patch

import requests
from requests.auth import HTTPBasicAuth

from amundsen_application.dashboard_preview.mode_preview import ModePreview, DEFAULT_REPORT_URL_TEMPLATE

ACCESS_TOKEN = 'token'
PASSWORD = 'password'
ORGANIZATION = 'foo'


class TestModePreview(unittest.TestCase):

    def test_get_preview_image(self) -> None:
        with patch.object(ModePreview, '_get_preview_image_url') as mock_get_preview_image_url,\
             patch.object(requests, 'get') as mock_get:
            mock_get_preview_image_url.return_value = 'http://foo.bar/image.jpeg'
            mock_get.return_value.content = b'bar'

            preview = ModePreview(access_token='token', password='password', organization='foo')

            mode_dashboard_uri = 'mode_dashboard://gold.dg/d_id'
            actual = preview.get_preview_image(uri=mode_dashboard_uri)

            self.assertEqual(b'bar', actual)
            mock_get.assert_called_with('http://foo.bar/image.jpeg', allow_redirects=True)

    def test_get_preview_image_url_success(self) -> None:
        with patch.object(requests, 'get') as mock_get:
            mock_get.return_value.json.return_value = {'web_preview_image': 'http://foo.bar/image.jpeg'}

            preview = ModePreview(access_token='token', password='password', organization='foo')
            mode_dashboard_uri = 'mode_dashboard://gold.dg/d_id'
            url = preview._get_preview_image_url(uri=mode_dashboard_uri)

            self.assertEqual(url, 'http://foo.bar/image.jpeg')

            expected_url = DEFAULT_REPORT_URL_TEMPLATE.format(organization=ORGANIZATION, dashboard_id='d_id')
            mock_get.assert_called_with(expected_url, auth=HTTPBasicAuth(ACCESS_TOKEN, PASSWORD))

    def test_get_preview_image_url_failure_none_value(self) -> None:
        with patch.object(requests, 'get') as mock_get:
            mock_get.return_value.json.return_value = {'web_preview_image': None}

            preview = ModePreview(access_token='token', password='password', organization='foo')
            mode_dashboard_uri = 'mode_dashboard://gold.dg/d_id'
            self.assertRaises(FileNotFoundError, preview._get_preview_image_url, uri=mode_dashboard_uri)

    def test_get_preview_image_url_failure_missing_key(self) -> None:
        with patch.object(requests, 'get') as mock_get:
            mock_get.return_value.json.return_value = {}

            preview = ModePreview(access_token='token', password='password', organization='foo')
            mode_dashboard_uri = 'mode_dashboard://gold.dg/d_id'
            self.assertRaises(FileNotFoundError, preview._get_preview_image_url, uri=mode_dashboard_uri)
