# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging
from typing import (
    Any, Iterator, Union,
)

import neo4j
from neo4j import Driver
from pyhocon import ConfigFactory, ConfigTree
from databuilder.databuilder.utils.neo4j import create_neo4j_driver

from databuilder.extractor.base_extractor import Extractor

LOGGER = logging.getLogger(__name__)


class Neo4jExtractor(Extractor):
    """
    Extractor to fetch records from Neo4j Graph database
    """
    CYPHER_QUERY_CONFIG_KEY = 'cypher_query'
    GRAPH_URL_CONFIG_KEY = 'graph_url'
    MODEL_CLASS_CONFIG_KEY = 'model_class'
    NEO4J_AUTH_USER = 'neo4j_auth_user'
    NEO4J_AUTH_PW = 'neo4j_auth_pw'
    NEO4J_DATABASE_NAME = 'neo4j_database'
    NEO4J_MAX_CONN_LIFE_TIME_SEC = 'neo4j_max_conn_life_time_sec'
    NEO4J_ENCRYPTED = 'neo4j_encrypted'
    """NEO4J_ENCRYPTED is a boolean indicating whether to use SSL/TLS when connecting."""
    NEO4J_VALIDATE_SSL = 'neo4j_validate_ssl'
    """NEO4J_VALIDATE_SSL is a boolean indicating whether to validate the server's SSL/TLS cert against system CAs."""
    NEO4J_DRIVER = 'neo4j_driver'

    DEFAULT_CONFIG = ConfigFactory.from_dict({
        NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
        NEO4J_DATABASE_NAME: neo4j.DEFAULT_DATABASE
    })

    def init(self, conf: ConfigTree) -> None:
        """
        Establish connections and import data model class if provided
        :param conf:
        """
        self.conf = conf.with_fallback(Neo4jExtractor.DEFAULT_CONFIG)
        self.graph_url = conf.get_string(Neo4jExtractor.GRAPH_URL_CONFIG_KEY)
        self.cypher_query = conf.get_string(Neo4jExtractor.CYPHER_QUERY_CONFIG_KEY)

        driver = conf.get(Neo4jExtractor.NEO4J_DRIVER, None)
        if driver and isinstance(driver, Driver):
            self.driver = driver
        elif driver and not isinstance(driver, Driver):
            msg = f'Driver should be of type neo4j.Driver, but an object of type {type(driver)} was given.'
            LOGGER.error(msg)
            raise TypeError(msg)
        else:
            self.driver = create_neo4j_driver(uri=self.graph_url,
                                              max_connection_lifetime=conf.get_int(
                                                  Neo4jExtractor.NEO4J_MAX_CONN_LIFE_TIME_SEC),
                                              auth=(conf.get_string(Neo4jExtractor.NEO4J_AUTH_USER),
                                                    conf.get_string(Neo4jExtractor.NEO4J_AUTH_PW)),
                                              validate_ssl=conf.get(Neo4jExtractor.NEO4J_VALIDATE_SSL, None),
                                              encrypted=conf.get(Neo4jExtractor.NEO4J_ENCRYPTED, None))

        self._extract_iter: Union[None, Iterator] = None

        model_class = conf.get(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY, None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)

    def close(self) -> None:
        """
        close connection to neo4j cluster
        """
        try:
            self.driver.close()
        except Exception as e:
            LOGGER.error("Exception encountered while closing the graph driver", e)

    def _execute_query(self, tx: Any) -> Any:
        """
        Create an iterator to execute sql.
        """
        LOGGER.info('Executing query %s', self.cypher_query)
        result = tx.run(self.cypher_query)
        return [record for record in result]

    def _get_extract_iter(self) -> Iterator[Any]:
        """
        Execute {cypher_query} and yield result one at a time
        """
        with self.driver.session(
            database=self.conf.get(Neo4jExtractor.NEO4J_DATABASE_NAME)
        ) as session:
            if not hasattr(self, 'results'):
                self.results = session.read_transaction(self._execute_query)

            for result in self.results:
                if hasattr(self, 'model_class'):
                    obj = self.model_class(**result)
                    yield obj
                else:
                    yield result

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
        return 'extractor.neo4j'
