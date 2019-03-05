import importlib
import logging
from typing import Any, Iterator, Union  # noqa: F401

from pyhocon import ConfigTree  # noqa: F401
from neo4j.v1 import GraphDatabase

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

    def init(self, conf):
        # type: (ConfigTree) -> None
        """
        Establish connections and import data model class if provided
        :param conf:
        """
        self.conf = conf
        self.graph_url = conf.get_string(Neo4jExtractor.GRAPH_URL_CONFIG_KEY)
        self.cypher_query = conf.get_string(Neo4jExtractor.CYPHER_QUERY_CONFIG_KEY)
        self.driver = self._get_driver()

        self._extract_iter = None  # type: Union[None, Iterator]

        model_class = conf.get(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY, None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)

    def close(self):
        # type: () -> None
        """
        close connection to neo4j cluster
        """
        try:
            self.driver.close()
        except Exception as e:
            LOGGER.error("Exception encountered while closing the graph driver", e)

    def _get_driver(self):
        # type: () -> Any
        """
        Create a Neo4j connection to Database
        """
        return GraphDatabase.driver(self.graph_url,
                                    auth=(self.conf.get_string(Neo4jExtractor.NEO4J_AUTH_USER),
                                          self.conf.get_string(Neo4jExtractor.NEO4J_AUTH_PW)))

    def _execute_query(self, tx):
        # type: (Any) -> Any
        """
        Create an iterator to execute sql.
        """
        LOGGER.info('Executing query {}'.format(self.cypher_query))
        result = tx.run(self.cypher_query)
        return result

    def _get_extract_iter(self):
        # type: () -> Iterator[Any]
        """
        Execute {cypher_query} and yield result one at a time
        """
        with self.driver.session() as session:
            if not hasattr(self, 'results'):
                self.results = session.read_transaction(self._execute_query)

            for result in self.results:
                if hasattr(self, 'model_class'):
                    obj = self.model_class(**result)
                    yield obj
                else:
                    yield result

    def extract(self):
        # type: () -> Any
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

    def get_scope(self):
        # type: () -> str
        return 'extractor.neo4j'
