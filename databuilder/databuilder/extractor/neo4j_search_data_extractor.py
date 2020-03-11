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
    ENTITY_TYPE = 'entity_type'

    DEFAULT_NEO4J_TABLE_CYPHER_QUERY = textwrap.dedent(
        """
        MATCH (db:Database)<-[:CLUSTER_OF]-(cluster:Cluster)
        <-[:SCHEMA_OF]-(schema:Schema)<-[:TABLE_OF]-(table:Table)
        {publish_tag_filter}
        OPTIONAL MATCH (table)-[:DESCRIPTION]->(table_description:Description)
        OPTIONAL MATCH (table)-[:TAGGED_BY]->(tags:Tag) WHERE tags.tag_type='default'
        WITH db, cluster, schema, table, table_description, COLLECT(DISTINCT tags.key) as tags
        OPTIONAL MATCH (table)-[:TAGGED_BY]->(badges:Tag) WHERE badges.tag_type='badge'
        WITH db, cluster, schema, table, table_description, tags, COLLECT(DISTINCT badges.key) as badges
        OPTIONAL MATCH (table)-[read:READ_BY]->(user:User)
        WITH db, cluster, schema, table, table_description, tags, badges, SUM(read.read_count) AS total_usage,
        COUNT(DISTINCT user.email) as unique_usage
        OPTIONAL MATCH (table)-[:COLUMN]->(col:Column)
        OPTIONAL MATCH (col)-[:DESCRIPTION]->(col_description:Description)
        WITH db, cluster, schema, table, table_description, tags, badges, total_usage, unique_usage,
        COLLECT(col.name) AS column_names, COLLECT(col_description.description) AS column_descriptions
        OPTIONAL MATCH (table)-[:LAST_UPDATED_AT]->(time_stamp:Timestamp)
        RETURN db.name as database, cluster.name AS cluster, schema.name AS schema,
        table.name AS name, table.key AS key, table_description.description AS description,
        time_stamp.last_updated_timestamp AS last_updated_timestamp,
        column_names,
        column_descriptions,
        total_usage,
        unique_usage,
        tags,
        badges
        ORDER BY table.name;
        """
    )

    DEFAULT_NEO4J_USER_CYPHER_QUERY = textwrap.dedent(
        """
        MATCH (user:User)
        OPTIONAL MATCH (user)-[read:READ]->(a)
        OPTIONAL MATCH (user)-[own:OWNER_OF]->(b)
        OPTIONAL MATCH (user)-[follow:FOLLOWED_BY]->(c)
        OPTIONAL MATCH (user)-[manage_by:MANAGE_BY]->(manager)
        {publish_tag_filter}
        with user, a, b, c, read, own, follow, manager
        where user.full_name is not null
        return user.email as email, user.first_name as first_name, user.last_name as last_name,
        user.full_name as full_name, user.github_username as github_username, user.team_name as team_name,
        user.employee_type as employee_type, manager.email as manager_email,
        user.slack_id as slack_id, user.is_active as is_active,
        REDUCE(sum_r = 0, r in COLLECT(DISTINCT read)| sum_r + r.read_count) AS total_read,
        count(distinct b) as total_own,
        count(distinct c) AS total_follow
        order by user.email
        """
    )

    # todo: 1. change total_read once we have the usage;
    #  2. add more fields once we have in the graph; 3. change mode to generic once add more support for dashboard
    DEFAULT_NEO4J_DASHBOARD_CYPHER_QUERY = textwrap.dedent(
        """
        MATCH (dashboard:Dashboard)
        OPTIONAL MATCH (dashboard)-[:DASHBOARD_OF]->(dbg:Dashboardgroup)
        OPTIONAL MATCH (dashboard)-[:DESCRIPTION]->(db_descr:Description)
        OPTIONAL MATCH (dbg)-[:DESCRIPTION]->(dbg_descr:Description)
        {publish_tag_filter}
        with dashboard, dbg, db_descr, dbg_descr
        where dashboard.name is not null
        return dbg.name as dashboard_group, dashboard.name as dashboard_name,
        coalesce(db_descr.description, '') as description,
        coalesce(dbg.description, '') as dashboard_group_description,
        'mode' as product,
        1 AS total_usage
        order by dbg.name
        """
    )

    # todo: we will add more once we add more entities
    DEFAULT_QUERY_BY_ENTITY = {
        'table': DEFAULT_NEO4J_TABLE_CYPHER_QUERY,
        'user': DEFAULT_NEO4J_USER_CYPHER_QUERY,
        'dashboard': DEFAULT_NEO4J_DASHBOARD_CYPHER_QUERY
    }

    def init(self, conf):
        # type: (ConfigTree) -> None
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
            if not hasattr(self, 'entity'):
                self.entity = 'table'
            publish_tag_filter = """WHERE {entity}.published_tag = '{tag}'""".format(entity=self.entity,
                                                                                     tag=publish_tag)
        return cypher_query.format(publish_tag_filter=publish_tag_filter)
