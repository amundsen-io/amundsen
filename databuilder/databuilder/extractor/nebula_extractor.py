# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import time
import random
import json

import importlib
import logging
from typing import (Any, Iterator, Union, List, TypeVar)

from functools import wraps

from nebula3.Config import Config as NebulaConfig
from nebula3.gclient.net import ConnectionPool, Session
from pyhocon import ConfigFactory, ConfigTree

from databuilder.extractor.base_extractor import Extractor

LOGGER = logging.getLogger(__name__)
T = TypeVar("T")


def retry(backoff_sec: int = 1) -> T:
    """
    An exponential backoff decorator
    :param fn: The function to be retried.
    :param backoff_sec: The time in second per each backoff step.
    """

    def decorator_retry(fn):

        @wraps(fn)
        def fn_retry(*args, **kwargs):
            attempts = 0
            _retry_num = args[0]._nebula_retry_number
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if attempts == _retry_num:
                        LOGGER.debug("[%s] %s attempts of retry exceeded.",
                                     fn.__name__, _retry_num)
                        raise e
                    else:
                        sleep = backoff_sec * 2**attempts + random.uniform(
                            0.8, 1.5)
                        LOGGER.debug(
                            "[%s] Retried for %s times, sleeping for %s seconds...",
                            fn.__name__,
                            attempts,
                            sleep,
                        )
                        time.sleep(sleep)
                        attempts += 1

        return fn_retry  # the decorator

    return decorator_retry


class NebulaQueryExecutionError(Exception):

    def __init__(self, code, errors):
        self.code = code
        self.errors = errors

    def __str__(self):
        return "Nebula Query Execution Error: " + str(self.code) + ", " + str(
            self.errors)


class NebulaExtractor(Extractor):
    """
    Extractor to fetch records from Nebula Graph database
    ToDo: support TLS
    """
    CYPHER_QUERY_CONFIG_KEY = 'cypher_query'
    GRAPH_URL_CONFIG_KEY = 'graph_url'
    MODEL_CLASS_CONFIG_KEY = 'model_class'
    NEBULA_MAX_CONN_LIFE_TIME_SEC = 'nebula_max_conn_life_time_sec'
    # Endpoint list for Nebula Graph e.g: "192.168.11.1:9669,192.168.11.2:9669"
    NEBULA_ENDPOINTS = "nebula_endpoints"
    NEBULA_MAX_CONN_POOL_SIZE = "nebula_max_conn_pool_size"

    NEBULA_AUTH_USER = 'nebula_auth_user'
    NEBULA_AUTH_PW = 'nebula_auth_pw'
    NEBULA_SPACE = "nebula_space"
    NEBULA_RETRY_NUMBER = "nebula_retry_number"

    DEFAULT_CONFIG = ConfigFactory.from_dict({
        NEBULA_MAX_CONN_POOL_SIZE: 50,
        NEBULA_SPACE: "amundsen",
        NEBULA_AUTH_USER: "root",
        NEBULA_AUTH_PW: "nebula",
        NEBULA_RETRY_NUMBER: 3,
    })

    def init(self, conf: ConfigTree) -> None:
        """
        Establish connections and import data model class if provided
        :param conf:
        """
        self.conf = conf.with_fallback(NebulaExtractor.DEFAULT_CONFIG)
        self.cypher_query = conf.get_string(
            NebulaExtractor.CYPHER_QUERY_CONFIG_KEY)

        self.connection_pool = self._get_connection_pool()

        self._extract_iter: Union[None, Iterator] = None

        model_class = conf.get(NebulaExtractor.MODEL_CLASS_CONFIG_KEY, None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)

    def close(self) -> None:
        """
        close connection to nebula cluster
        """
        try:
            self.connection_pool.close()
        except Exception as e:
            LOGGER.error(
                "Exception encountered while closing the Nebula Graph Connection", e)

    def _get_connection_pool(self) -> Any:
        """
        Create a Nebula connection to Database
        """
        self._nebula_space = self.conf.get_string(NebulaExtractor.NEBULA_SPACE)
        self._nebula_max_conn_pool_size = self.conf.get_int(
            NebulaExtractor.NEBULA_MAX_CONN_POOL_SIZE)
        self._nebula_endpoints = self.conf.get_string(
            NebulaExtractor.NEBULA_ENDPOINTS)
        self._nebula_credential = (
            self.conf.get_string(NebulaExtractor.NEBULA_AUTH_USER),
            self.conf.get_string(NebulaExtractor.NEBULA_AUTH_PW),
        )

        self._nebula_retry_number = self.conf.get_int(
            NebulaExtractor.NEBULA_RETRY_NUMBER)

        connection_pool = ConnectionPool()
        config = NebulaConfig()
        config.max_connection_pool_size = self._nebula_max_conn_pool_size

        self.nebula_endpoints = [(e.split(":")[0], int(e.split(":")[1]))
                                 for e in self._nebula_endpoints.split(",")
                                 if e]

        connection_pool.init(self.nebula_endpoints, config)
        with connection_pool.session_context(
                *self._nebula_credential) as session:
            self._space_query = f"USE {self._nebula_space};"
            # This is a probe to see if the Nebula Graph is ready and its space exists
            self._execute_query(self._space_query, session)
        return connection_pool

    @staticmethod
    def _decode_json_result(raw_data: bytes) -> List:
        """
        Decode the raw bytes data into a list of dicts.
        :param raw_data:
        :return:
        """
        result_dict = json.loads(raw_data)
        return result_dict.get('results',
                           []), result_dict.get('errors',
                                                [{}])[0].get('code', -1)

    def _execute_query(self, query: str, session: Session) -> List:
        """
        :param query:
        :param session:
        :return:
        """
        try:
            r = session.execute_json(f"{self._space_query} {query}")
            results, r_code = self._decode_json_result(r)
            if r_code != 0:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    errors = results[0].get('errors', '')
                    LOGGER.debug(
                        "Failed executing query: %s, errors: %s, results: %s",
                        query, errors, results[0])
                raise NebulaQueryExecutionError(r_code,
                                                results[0].get('errors', ''))
            return results

        except Exception as e:
            if LOGGER.isEnabledFor(logging.DEBUG):
                LOGGER.debug('Failed executing query: %s, except: %s', query,
                             str(e))
            LOGGER.error('Failed executing query: %s', query)
            raise RuntimeError(str(e))

    def _get_extract_iter(self) -> Iterator[Any]:
        """
        Execute {cypher_query} and yield result one at a time
        """
        with self.connection_pool.session_context(
                *self._nebula_credential) as session:
            self.results = self._execute_query(self.cypher_query, session)[0]
            self.result_keys = self.results['columns']

            for result in self.results['data']:
                # check length of result and self.result_keys to be equal
                if len(result['row']) != len(self.result_keys):
                    raise RuntimeError(
                        f"Length of result row ({result['row']}) and result_keys ({self.result_keys}) are not equal"
                    )
                record = dict(zip(self.result_keys, result['row']))
                if hasattr(self, 'model_class'):
                    obj = self.model_class(**record)
                    yield obj
                else:
                    yield record

    def extract(self) -> Any:
        """
        Return {result} object as it is or convert to object of
        {model_class}, if specified.
        """
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()

        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def get_scope(self) -> str:
        return 'extractor.nebula'
