# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from gremlin_python.driver.transport import AbstractBaseTransport
import mocket.mocket
import mocket.mockhttp
from overrides import overrides
import os
from requests import PreparedRequest
from requests_aws4auth import AWS4Auth
import threading
from typing import Any, Callable, List, Mapping, Optional, Tuple, TypeVar, Union
from urllib.parse import urlparse
from websocket import create_connection


__all__ = ["WebsocketClientTransport", "Aws4AuthWebsocketTransport"]


def monkey_patch_mocket() -> None:
    # monkey patch this method since the existing behavior is really broken
    T = TypeVar('T', bound=mocket.mocket.MocketSocket)

    def monkey_fileno(self: T) -> int:
        if mocket.mocket.Mocket.r_fd is None and mocket.mocket.Mocket.w_fd is None:
            mocket.mocket.Mocket.r_fd, mocket.mocket.Mocket.w_fd = os.pipe()
        return mocket.mocket.Mocket.r_fd

    mocket.mocket.MocketSocket.fileno = monkey_fileno


monkey_patch_mocket()


class SelfRecordingWebSocketEntry(mocket.mocket.MocketEntry):
    """
    This is like  mocket.mockhttp.Entry, but it is less picky about the data and records locally.
    """
    request_cls = mocket.mockhttp.Request
    response_cls = mocket.mockhttp.Response

    def __init__(self, host: str, port: int, responses: Any) -> None:
        self.host: str = host
        self.port: int = port
        self._data: List[bytes] = []
        self._data_lock = threading.Lock()
        super(SelfRecordingWebSocketEntry, self).__init__(location=(host, port), responses=responses)

    @overrides
    def collect(self, data: bytes) -> None:
        with self._data_lock:
            self._data.append(data)

    def get_data(self) -> bytes:
        with self._data_lock:
            return b''.join(self._data)

    @classmethod
    def register(cls, *, uri: str, body: str = '', status: int = 101,
                 headers: Mapping[str, str] = {'Connection': 'Upgrade', 'Upgrade': 'WebSocket'}) \
            -> 'SelfRecordingWebSocketEntry':
        host, port = cls.host_and_port(uri)
        entry = cls(host, port, cls.response_cls(body=body, status=status, headers=headers))
        mocket.Mocket.register(entry)
        return entry

    @classmethod
    def host_and_port(cls, uri: str) -> Tuple[str, int]:
        parsed = urlparse(uri)
        return (parsed.hostname, parsed.port or (443 if parsed.scheme.endswith('s') else 80))


V = TypeVar('V')


class WebsocketClientTransport(AbstractBaseTransport):
    """
    An AbstractBaseTransport based on the websocket-client library instead of Tornado
    """  # noqa

    def __init__(self, *, extra_websocket_options: Mapping[str, Any] = {}) -> None:
        self.extra_websocket_options: Mapping[str, str] = extra_websocket_options
        self._connection_lock = threading.Lock()
        self._connection = None
        self._connected: bool = False
        self._headers: Optional[Mapping[str, Any]] = None
        self._url: str = None
        super().__init__()

    @overrides
    def connect(self, url: str, headers: Optional[Mapping[str, Any]] = None) -> None:
        if not self.closed():
            raise RuntimeError(f'already connected!')
        with self._connection_lock:
            self._url = url
            # later this gets used and *mutated* even if empty now, so make a copy so we're not touching the caller's
            # data
            self._headers = dict() if headers is None else dict(headers)
            self._connected = True
            self._ensure_connect_or_raise()

    @overrides
    def write(self, message: Union[str, bytes]) -> None:
        if isinstance(message, bytes):
            def write() -> None:
                self._connection.send_binary(message)
        elif isinstance(message, str):
            # send text
            def write() -> None:
                self._connection.send(message)
        else:
            # what is it?
            raise RuntimeError(f'''got a message that is neither a str nor bytes: {type(message)}''')
        with self._connection_lock:
            self._ensure_connect_or_raise()
            self._run_except(write)

    @overrides
    def read(self) -> Union[str, bytes]:
        data = None
        with self._connection_lock:
            self._ensure_connect_or_raise()
            data = self._run_except(self._connection.recv)
        # always return bytes.  the client will decode for us if it's a text message
        # but using recv_data() seems wrong since it skips the readlock
        if isinstance(data, str):
            data = data.encode('utf-8')
        return data

    @overrides
    def close(self) -> None:
        with self._connection_lock:
            self._connected = False
            try:
                if self._connection is not None and not self._connection.closed():
                    self._connection.close()
            finally:
                self._connection = None

    @overrides
    def closed(self) -> bool:
        with self._connection_lock:
            return not self._connected and (self._connection is None or self._connection.closed())

    def _ensure_connect_or_raise(self) -> None:
        assert self._connection_lock.locked(), f'not locked!'

        if self._connection is not None:
            return
        if not self._connected:
            raise RuntimeError(f'connection is closed!')
        try:
            self._connection = create_connection(url=self._url, header=self._headers, **self.extra_websocket_options)
        except Exception:
            self._connection = None
            raise

        assert self._connection is not None, f'connection is closed!'

    def _run_except(self, callable: Callable[[], V]) -> V:
        """
        if exception is raised:
           close the connection
           let the exception bubble up
           set a flag allowing reconnect
        """
        assert self._connection_lock.locked(), f'not locked!'
        try:
            return callable()
        except Exception:
            # what is it? close
            try:
                if self._connection is not None and not self._connection.closed():
                    self._connection.close()
            except Exception:
                # close quietly
                pass
            finally:
                self._connection = None
            # raise the original
            raise


class Aws4AuthWebsocketTransport(WebsocketClientTransport):
    """

    This is super janky/awesome.  We don't have a good hook like netty (java, big on pipelines) or
    requests (which doesn't do websockets, but positions the authenticator at the end of the
    processesing and esssentially asks it to just return a new request that's properly
    authenticated).  What we do is use a mocking library (usually used for testing...) fake the
    websockets handshake request, and use that to construct the proper headers with AWS4Auth and
    then add those to a real websockets handshake.


    Where could this go wrong? Mocket seems a little exciting, so that's a good spot to start if we
    didn't get a raw request back. (There's an exception for that.)

    >>> from aws4authwebsocket.transport import Aws4AuthWebsocketTransport
    >>> factory = lambda: Aws4AuthWebsocketTransport(aws_access_key_id=secret['aws_access_key_id'], aws_secret_access_key=secret['aws_secret_access_key'], service_region=secret['service_region'])
    >>> url = WHATEVER_URL
    >>> g = GraphTraversalSource = Graph().traversal().withRemote(DriverRemoteConnection(url=url, traversal_source='g', transport_factory=factory, websocket_options=dict(http_proxy_host='stupid', http_no_proxy=[urllib.parse.urlparse(url).hostname])))
    >>>
    """  # noqa

    def __init__(self, *, aws_access_key_id: str, aws_secret_access_key: str, service_region: str,
                 service_name: str = 'neptune-db', extra_aws4auth_options: Mapping[str, Any] = {},
                 extra_websocket_options: Mapping[str, Any] = {}) -> None:
        # override any of these extra options (because we rely on their behavior)
        extra_aws4auth_options = dict(extra_aws4auth_options)
        extra_aws4auth_options.update(include_hdrs='*', raise_invalid_date=True)
        self.aws4auth = AWS4Auth(
            aws_access_key_id, aws_secret_access_key, service_region, service_name, **extra_aws4auth_options)
        super().__init__(extra_websocket_options=extra_websocket_options)

    def _make_extra_headers(self, url: str, headers: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Returns the headers we should pass for this request.  This includes both the AWS v4 signature
        authentication ones as well as the Sec-WebSocket-* ones (which might vary and mess up the signatures used in
        authentication)
        """
        raw_request: bytes = self._get_raw_request_for(url=url, header=headers, **self.extra_websocket_options)
        request: PreparedRequest = self._parse_raw_request(raw_request)
        before_auth = set([k.lower() for k in request.headers.keys()])
        # we're always supposed to exclude these but AWS4Auth will include them with include_hdrs='*', so just delete
        # from the fake PreparedRequest we pass to AWS4Auth
        for k in set(request.headers.keys()):
            if k.lower() in ('connection', 'x-amzn-trace-id'):
                del request.headers[k]
        # usually mutates request (contract is to return it though, so cover our bases)
        request = self.aws4auth(request)
        # keep header if added by websocket client or aws4auth
        extra_headers = dict()
        for k, v in request.headers.items():
            if k.lower() not in before_auth or k.lower().startswith('sec-websocket'):
                extra_headers[k] = v
        return extra_headers

    @classmethod
    def _get_raw_request_for(cls, url: str, *args: Any, **kwargs: Any) -> bytes:
        """
        args are passed to websocket.create_connection, and then we get the request data returned.
        """
        # we fake a response to the handshake, just so we can get the request
        entry = SelfRecordingWebSocketEntry.register(uri=url)
        exception: Optional[Exception] = None     # noqa: E701
        # TODO: should fail if Mocketizer already enabled
        with mocket.Mocketizer():
            ws = None
            try:
                ws = create_connection(url=url, *args, **kwargs)
            except Exception as e:
                exception = e
            finally:
                if ws is not None:
                    try:
                        ws.close()
                    except Exception:
                        pass
        # return the request we got
        data = entry.get_data()
        if data is not None and len(data) > 0:
            return data
        elif exception is not None:
            raise exception
        else:
            raise RuntimeError(f'We did not get a raw request back from our attempts to fake a handshake to {url}, nor'
                               f'did we get an exception')

    @classmethod
    def _parse_raw_request(cls, raw_request: bytes) -> PreparedRequest:
        """
        ok, this is kind of janky, but AWS4Auth is meant to work with requests, so expects a PreparedRequest
        """
        body: Optional[str] = None
        headers, body = raw_request.decode('utf-8').split('\r\n\r\n', 1)
        # strip the trailing \r\n if present
        if len(body) == 0:
            body = None
        elif body.endswith('\r\n'):
            body = body[:-2]
        # hi!  if you get here looking for folded headers, that's obsolete and we ought not be generating them
        method_et_al, headers = headers.split('\r\n', 1)
        headers_as_dict: Mapping[str, str] = \
            dict([(k.strip(), v.strip()) for k, v in [h.split(':', 1) for h in headers.split('\r\n')]])
        # this is a little janky, really should be one or more spaces
        method, path_et_al, version = method_et_al.split(' ', 2)
        # this is very sketchy looking but I promise that we don't care about the host, port, or scheme here
        url = 'https://nope/' + path_et_al
        req = PreparedRequest()
        req.prepare_method(method)
        req.prepare_url(url, {})
        req.prepare_headers(headers_as_dict)
        req.prepare_body(data=body, files=None)
        # don't req.prepare_content_length, we already had that in headers surely
        return req

    @overrides
    def connect(self, url: str, headers: Mapping[str, Any] = None) -> None:
        _headers = dict(headers) if headers is not None else dict()
        extra_headers = self._make_extra_headers(url, _headers)
        _headers.update(extra_headers)
        # TODO: should add use http_no_proxy so you don't have to del from os.eviron
        super().connect(url, _headers)
