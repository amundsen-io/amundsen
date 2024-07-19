# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging
from typing import (
    Any, Iterator, Union,
)

import neo4j
from neo4j import GraphDatabase
from neo4j.api import (
    SECURITY_TYPE_SECURE, SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, parse_neo4j_uri,
)
from pyhocon import ConfigFactory, ConfigTree

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
    # in Neo4j (v4.0+), we can create and use more than one active database at the same time
    NEO4J_DATABASE_NAME = 'neo4j_database'
    NEO4J_MAX_CONN_LIFE_TIME_SEC = 'neo4j_max_conn_life_time_sec'
    NEO4J_ENCRYPTED = 'neo4j_encrypted'
    """NEO4J_ENCRYPTED is a boolean indicating whether to use SSL/TLS when connecting."""
    NEO4J_VALIDATE_SSL = 'neo4j_validate_ssl'
    """NEO4J_VALIDATE_SSL is a boolean indicating whether to validate the server's SSL/TLS cert against system CAs."""

    DEFAULT_CONFIG = ConfigFactory.from_dict({
        NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
        NEO4J_DATABASE_NAME: neo4j.DEFAULT_DATABASE,
    })

    def init(self, conf: ConfigTree) -> None:
        """
        Establish connections and import data model class if provided
        :param conf:
        """
        self.conf = conf.with_fallback(Neo4jExtractor.DEFAULT_CONFIG)
        self.graph_url = self.conf.get_string(Neo4jExtractor.GRAPH_URL_CONFIG_KEY)
        self.cypher_query = self.conf.get_string(Neo4jExtractor.CYPHER_QUERY_CONFIG_KEY)
        self.db_name = self.conf.get_string(Neo4jExtractor.NEO4J_DATABASE_NAME)

        uri = self.conf.get_string(Neo4jExtractor.GRAPH_URL_CONFIG_KEY)
        driver_args = {
            'uri': uri,
            'max_connection_lifetime': self.conf.get_int(Neo4jExtractor.NEO4J_MAX_CONN_LIFE_TIME_SEC),
            'auth': (self.conf.get_string(Neo4jExtractor.NEO4J_AUTH_USER),
                     self.conf.get_string(Neo4jExtractor.NEO4J_AUTH_PW)),
        }

        # if URI scheme not secure set `trust`` and `encrypted` to default values
        # https://neo4j.com/docs/api/python-driver/current/api.html#uri
        _, security_type, _ = parse_neo4j_uri(uri=uri)
        if security_type not in [SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, SECURITY_TYPE_SECURE]:
            default_security_conf = {'trust': neo4j.TRUST_ALL_CERTIFICATES, 'encrypted': True}
            driver_args.update(default_security_conf)

        # if NEO4J_VALIDATE_SSL or NEO4J_ENCRYPTED are set in config pass them to the driver
        validate_ssl_conf = self.conf.get(Neo4jExtractor.NEO4J_VALIDATE_SSL, None)
        encrypted_conf = self.conf.get(Neo4jExtractor.NEO4J_ENCRYPTED, None)
        if validate_ssl_conf is not None:
            driver_args['trust'] = neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES if validate_ssl_conf \
                else neo4j.TRUST_ALL_CERTIFICATES
        if encrypted_conf is not None:
            driver_args['encrypted'] = encrypted_conf

        self.driver = GraphDatabase.driver(**driver_args)

        self._extract_iter: Union[None, Iterator] = None

        model_class = self.conf.get(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY, None)
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
            database=self.db_name
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
