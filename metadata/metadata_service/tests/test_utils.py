from flask import Response

from metadata_service.config import LocalConfig


def after_request_func(resp: Response) -> Response:
    resp.headers['test_header'] = '123'
    return resp


class TestHookConfig(LocalConfig):
    AFTER_REQUEST_HOOK = after_request_func
