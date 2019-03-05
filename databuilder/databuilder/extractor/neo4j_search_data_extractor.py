import textwrap
from typing import Any  # noqa: F401

from pyhocon import ConfigTree  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.publisher.neo4j_csv_publisher import JOB_PUBLISH_TAG


class Neo4jSearchDataExtractor(Extractor):
    """
    Extractor to fetch data required to support search from Neo4j graph database
    Use Neo4jExtractor extractor class
    """
    CYPHER_QUERY_CONFIG_KEY = 'cypher_query'

    DEFAULT_NEO4J_CYPHER_QUERY = textwrap.dedent(
        """
        MATCH (db:Database)<-[:CLUSTER_OF]-(cluster:Cluster)<-[:SCHEMA_OF]-(schema:Schema)<-[:TABLE_OF]-(table:Table)
        {publish_tag_filter}
        OPTIONAL MATCH (table)-[:DESCRIPTION]->(table_description:Description)
        OPTIONAL MATCH (table)-[read:READ_BY]->(user:User)
        OPTIONAL MATCH (table)-[:COLUMN]->(cols:Column)
        OPTIONAL MATCH (cols)-[:DESCRIPTION]->(col_description:Description)
        OPTIONAL MATCH (table)-[:TAGGED_BY]->(tags:Tag)
        OPTIONAL MATCH (table)-[:LAST_UPDATED_AT]->(time_stamp:Timestamp)
        RETURN db.name as database, cluster.name AS cluster, schema.name AS schema_name,
        table.name AS table_name, table.key AS table_key, table_description.description AS table_description,
        time_stamp.last_updated_timestamp AS table_last_updated_epoch,
        EXTRACT(c in COLLECT(DISTINCT cols)| c.name) AS column_names,
        EXTRACT(cd IN COLLECT(DISTINCT col_description)| cd.description) AS column_descriptions,
        REDUCE(sum_r = 0, r in COLLECT(DISTINCT read)| sum_r + r.read_count) AS total_usage,
        COUNT(DISTINCT user.email) as unique_usage,
        COLLECT(DISTINCT tags.key) as tag_names
        ORDER BY table.name;
        """
    )

    def init(self, conf):
        # type: (ConfigTree) -> None
        """
        Initialize Neo4jExtractor object from configuration and use that for extraction
        """
        self.conf = conf

        # extract cypher query from conf, if specified, else use default query
        if Neo4jSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY in conf:
            self.cypher_query = conf.get_string(Neo4jSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY)
        else:
            self.cypher_query = self._add_publish_tag_filter(conf.get_string(JOB_PUBLISH_TAG, ''),
                                                             Neo4jSearchDataExtractor.DEFAULT_NEO4J_CYPHER_QUERY)

        self.neo4j_extractor = Neo4jExtractor()
        # write the cypher query in configs in Neo4jExtractor scope
        key = self.neo4j_extractor.get_scope() + '.' + Neo4jExtractor.CYPHER_QUERY_CONFIG_KEY
        self.conf.put(key, self.cypher_query)
        # initialize neo4j_extractor from configs
        self.neo4j_extractor.init(Scoped.get_scoped_conf(self.conf, self.neo4j_extractor.get_scope()))

    def close(self):
        # type: () -> None
        """
        Use close() method specified by neo4j_extractor
        to close connection to neo4j cluster
        """
        self.neo4j_extractor.close()

    def extract(self):
        # type: () -> Any
        """
        Invoke extract() method defined by neo4j_extractor
        """
        return self.neo4j_extractor.extract()

    def get_scope(self):
        # type: () -> str
        return 'extractor.search_data'

    def _add_publish_tag_filter(self, publish_tag, cypher_query):
        """
        Adds publish tag filter into Cypher query
        :param publish_tag: value of publish tag.
        :param cypher_query:
        :return:
        """
        # type: (str, str) -> str
        if not publish_tag:
            publish_tag_filter = ''
        else:
            publish_tag_filter = """WHERE table.published_tag = '{}'""".format(publish_tag)

        return cypher_query.format(publish_tag_filter=publish_tag_filter)
