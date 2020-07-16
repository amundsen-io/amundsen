# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from metadata_service.proxy.aws4authwebsocket.transport import Aws4AuthWebsocketTransport
import unittest


class TestAws4AuthWebsocketTransport(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'wss://xxxxxnotreallyawsxxxxxxxx.com:8182/gremlin'
        self.aws_access_key_id = 'test_key'
        self.aws_secret_access_key = 'test_secret_key'
        self.service_region = 'test_region'

    def test_get_raw_request(self) -> None:
        """
        tests our Mocket usage and the exception handling
        """
        raw_request = Aws4AuthWebsocketTransport._get_raw_request_for(self.url)
        prepared_request = Aws4AuthWebsocketTransport._parse_raw_request(raw_request)
        self.assertEqual(
            set(prepared_request.headers.keys()),
            set(['Host', 'Origin', 'Connection', 'Upgrade', 'Sec-WebSocket-Key', 'Sec-WebSocket-Version']))

    def test_get_raw_request_uses_headers(self) -> None:
        raw_request = Aws4AuthWebsocketTransport._get_raw_request_for(
            self.url, header={'Foo': 'Bar', 'Sec-WebSocket-Key': 'xxxxxxxxxxxxxx'})
        prepared_request = Aws4AuthWebsocketTransport._parse_raw_request(raw_request)
        self.assertEqual(
            set(prepared_request.headers.keys()),
            set(['Host', 'Origin', 'Connection', 'Upgrade', 'Sec-WebSocket-Key', 'Sec-WebSocket-Version', 'Foo']))
        self.assertEqual(prepared_request.headers['Foo'], 'Bar')
        self.assertEqual(prepared_request.headers['Sec-WebSocket-Key'], 'xxxxxxxxxxxxxx')

    def test_get_raw_request_yields_exception(self) -> None:
        """
        tests the exception handling
        """
        try:
            Aws4AuthWebsocketTransport._get_raw_request_for(self.url, class_=None)
            self.assertEqual("did not raise an exception!", "")
        except Exception as e:
            # the particular exception we're causing is a that we passed None to a thing expecting a
            # constructor/factory/callable
            self.assertIsInstance(e, TypeError)
            self.assertEqual(e.args[0].endswith('object is not callable'), True)

    def test_make_extra_headers(self) -> None:
        transport = Aws4AuthWebsocketTransport(
            aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key,
            service_region=self.service_region)
        extra_headers = transport._make_extra_headers(self.url, {'Foo': 'Bar'})
        self.assertEqual(
            set(extra_headers.keys()),
            set(['Authorization', 'Sec-WebSocket-Version', 'Sec-WebSocket-Key', 'x-amz-date', 'x-amz-content-sha256']))

    def test_make_extra_headers_aws4auth(self) -> None:
        transport = Aws4AuthWebsocketTransport(
            aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key,
            service_region=self.service_region)
        # usually you would not pass in the key (because it's a bad idea) and date (because it gets validated for
        # freshness by the server, because it's a bad idea to let these get replayed)
        extra_headers = transport._make_extra_headers(
            self.url, {'Foo': 'Bar', 'Sec-WebSocket-Key': 'test_websocket_key', 'x-amz-date': '20191113T212041Z'})
        self.assertEqual(
            set(extra_headers.keys()),
            set(['Authorization', 'Sec-WebSocket-Version', 'Sec-WebSocket-Key', 'x-amz-content-sha256']))
        self.assertEqual(extra_headers['Sec-WebSocket-Key'], 'test_websocket_key')
        self.assertEqual(extra_headers['Authorization'], 'AWS4-HMAC-SHA256 Credential=test_key/20191113/test_region/neptune-db/aws4_request, SignedHeaders=foo;host;origin;sec-websocket-key;sec-websocket-version;upgrade;x-amz-content-sha256;x-amz-date, Signature=d27dbb7ddf77b0d73eee9df28c635640b7eb320aa8c70c35d17bb39f531044ba')  # noqa: E501
