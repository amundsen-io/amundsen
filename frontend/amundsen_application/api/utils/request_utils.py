from typing import Dict

import requests
from flask import current_app as app

REQUEST_SESSION_TIMEOUT_SEC = 3


def get_query_param(args: Dict, param: str, error_msg: str = None) -> str:
    value = args.get(param)
    if value is None:
        msg = 'A {0} parameter must be provided'.format(param) if error_msg is not None else error_msg
        raise Exception(msg)
    return value


def request_metadata(*,     # type: ignore
                     url: str,
                     method: str = 'GET',
                     timeout_sec: int = REQUEST_SESSION_TIMEOUT_SEC):
    """
    Helper function to make a request to metadata service.
    Sets the client and header information based on the configuration
    :param method: DELETE | GET | POST | PUT
    :param url: The request URL
    :param timeout_sec: Number of seconds before timeout is triggered.
    :return:
    """
    if app.config['REQUEST_HEADERS_METHOD']:
        headers = app.config['REQUEST_HEADERS_METHOD'](app)
    else:
        headers = app.config['METADATASERVICE_REQUEST_HEADERS']
    return request_wrapper(method=method,
                           url=url,
                           client=app.config['METADATASERVICE_REQUEST_CLIENT'],
                           headers=headers,
                           timeout_sec=timeout_sec)


def request_search(*,     # type: ignore
                   url: str,
                   method: str = 'GET',
                   timeout_sec: int = REQUEST_SESSION_TIMEOUT_SEC):
    """
    Helper function to make a request to search service.
    Sets the client and header information based on the configuration
    :param method: DELETE | GET | POST | PUT
    :param url: The request URL
    :param timeout_sec: Number of seconds before timeout is triggered.
    :return:
    """
    if app.config['REQUEST_HEADERS_METHOD']:
        headers = app.config['REQUEST_HEADERS_METHOD'](app)
    else:
        headers = app.config['SEARCHSERVICE_REQUEST_HEADERS']
    return request_wrapper(method=method,
                           url=url,
                           client=app.config['SEARCHSERVICE_REQUEST_CLIENT'],
                           headers=headers,
                           timeout_sec=timeout_sec)


# TODO: Define an interface for envoy_client
def request_wrapper(method: str, url: str, client, headers, timeout_sec: int):  # type: ignore
    """
    Wraps a request to use Envoy client and headers, if available
    :param method: DELETE | GET | POST | PUT
    :param url: The request URL
    :param client: Optional Envoy client
    :param headers: Optional Envoy request headers
    :param timeout_sec: Number of seconds before timeout is triggered. Not used with Envoy
    :return:
    """
    if client is not None:
        if method == 'DELETE':
            return client.delete(url, headers=headers, raw_response=True)
        elif method == 'GET':
            return client.get(url, headers=headers, raw_response=True)
        elif method == 'POST':
            return client.post(url, headers=headers, raw_response=True)
        elif method == 'PUT':
            return client.put(url, headers=headers, raw_response=True)
        else:
            raise Exception('Method not allowed: {}'.format(method))
    else:
        with requests.Session() as s:
            if method == 'DELETE':
                return s.delete(url, headers=headers, timeout=timeout_sec)
            elif method == 'GET':
                return s.get(url, headers=headers, timeout=timeout_sec)
            elif method == 'POST':
                return s.post(url, headers=headers, timeout=timeout_sec)
            elif method == 'PUT':
                return s.put(url, headers=headers, timeout=timeout_sec)
            else:
                raise Exception('Method not allowed: {}'.format(method))
