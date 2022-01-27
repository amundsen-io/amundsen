# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import textwrap
from typing import Any

from pyhocon import ConfigTree

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.publisher.neo4j_csv_publisher import JOB_PUBLISH_TAG
from databuilder.task.search.search_data_queries import DEFAULT_NEO4J_TABLE_CYPHER_QUERY, DEFAULT_NEO4J_DASHBOARD_CYPHER_QUERY, DEFAULT_NEO4J_FEATURE_CYPHER_QUERY, DEFAULT_NEO4J_USER_CYPHER_QUERY


class Neo4jSearchDataExtractor(Extractor):
    """
    Extractor to fetch data required to support search from Neo4j graph database
    Use Neo4jExtractor extractor class
    """
    CYPHER_QUERY_CONFIG_KEY = 'cypher_query'
    ENTITY_TYPE = 'entity_type'

    DEFAULT_QUERY_BY_ENTITY = {
        'table': DEFAULT_NEO4J_TABLE_CYPHER_QUERY,
        'user': DEFAULT_NEO4J_USER_CYPHER_QUERY,
        'dashboard': DEFAULT_NEO4J_DASHBOARD_CYPHER_QUERY,
        'feature': DEFAULT_NEO4J_FEATURE_CYPHER_QUERY,
    }

    def init(self, conf: ConfigTree) -> None:
        """
        Initialize Neo4jExtractor object from configuration and use that for extraction
        """
        self.conf = conf
        self.entity = conf.get_string(Neo4jSearchDataExtractor.ENTITY_TYPE, default='table').lower()
        # extract cypher query from conf, if specified, else use default query
        if Neo4jSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY in conf:
            self.cypher_query = conf.get_string(Neo4jSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY)
        else:
            default_query = Neo4jSearchDataExtractor.DEFAULT_QUERY_BY_ENTITY[self.entity]
            self.cypher_query = self._add_publish_tag_filter(conf.get_string(JOB_PUBLISH_TAG, ''),
                                                             cypher_query=default_query)

        self.neo4j_extractor = Neo4jExtractor()
        # write the cypher query in configs in Neo4jExtractor scope
        key = self.neo4j_extractor.get_scope() + '.' + Neo4jExtractor.CYPHER_QUERY_CONFIG_KEY
        self.conf.put(key, self.cypher_query)
        # initialize neo4j_extractor from configs
        self.neo4j_extractor.init(Scoped.get_scoped_conf(self.conf, self.neo4j_extractor.get_scope()))

    def close(self) -> None:
        """
        Use close() method specified by neo4j_extractor
        to close connection to neo4j cluster
        """
        self.neo4j_extractor.close()

    def extract(self) -> Any:
        """
        Invoke extract() method defined by neo4j_extractor
        """
        return self.neo4j_extractor.extract()

    def get_scope(self) -> str:
        return 'extractor.search_data'

    def _add_publish_tag_filter(self, publish_tag: str, cypher_query: str) -> str:
        """
        Adds publish tag filter into Cypher query
        :param publish_tag: value of publish tag.
        :param cypher_query:
        :return:
        """

        if not publish_tag:
            publish_tag_filter = ''
        else:
            if not hasattr(self, 'entity'):
                self.entity = 'table'
            publish_tag_filter = f"WHERE {self.entity}.published_tag = '{publish_tag}'"
        return cypher_query.format(publish_tag_filter=publish_tag_filter)
