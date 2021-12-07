# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import textwrap
from typing import Any

from pyhocon import ConfigTree

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.nebula_extractor import NebulaExtractor
from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.feature.feature_metadata import FeatureMetadata
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.user import User as UserMetadata
from databuilder.publisher.nebula_csv_publisher import JOB_PUBLISH_TAG


class NebulaSearchDataExtractor(Extractor):
    """
    Extractor to fetch data required to support search from Nebula graph database
    Use NebulaExtractor extractor class
    """
    CYPHER_QUERY_CONFIG_KEY = 'cypher_query'
    ENTITY_TYPE = 'entity_type'

    DEFAULT_NEBULA_TABLE_CYPHER_QUERY = textwrap.dedent("""
        MATCH (db:Database)<-[:CLUSTER_OF]-(cluster:Cluster)
        <-[:SCHEMA_OF]-(schema:Schema)<-[:TABLE_OF]-(table:Table)
        {publish_tag_filter}
        OPTIONAL MATCH (table)-[:DESCRIPTION]->(table_description:Description)
        OPTIONAL MATCH (schema)-[:DESCRIPTION]->(schema_description:Description)
        OPTIONAL MATCH (table)-[:DESCRIPTION]->(prog_descs:Programmatic_Description)
        WITH db, cluster, schema, schema_description, table, table_description,
        COLLECT(prog_descs.Programmatic_Description.description) AS programmatic_descriptions
        OPTIONAL MATCH (table)-[:TAGGED_BY]->(`tags`:`Tag`) WHERE `tags`.`Tag`.tag_type=='default'
        WITH db, cluster, schema, schema_description, table, table_description, programmatic_descriptions,
        COLLECT(DISTINCT id(`tags`)) AS `tags`
        OPTIONAL MATCH (table)-[:HAS_BADGE]->(badges:Badge)
        WITH db, cluster, schema, schema_description, table, table_description, programmatic_descriptions, `tags`,
        COLLECT(DISTINCT id(`badges`)) AS badges
        OPTIONAL MATCH (table)-[read:READ_BY]->(`user`:`User`)
        WITH db, cluster, schema, schema_description, table, table_description, programmatic_descriptions, `tags`, badges,
        SUM(read.read_count) AS total_usage,
        COUNT(DISTINCT `user`.`User`.email) AS unique_usage
        OPTIONAL MATCH (table)-[:COLUMN]->(col:Column)
        OPTIONAL MATCH (col)-[:DESCRIPTION]->(col_description:Description)
        WITH db, cluster, schema, schema_description, table, table_description, `tags`, badges, total_usage, unique_usage,
        programmatic_descriptions,
        COLLECT(col.Column.name) AS column_names, COLLECT(col_description.Description.description) AS column_descriptions
        OPTIONAL MATCH (table)-[:LAST_UPDATED_AT]->(time_stamp:`Timestamp`)
        RETURN db.Database.name as database, cluster.Cluster.name AS cluster, schema.Schema.name AS schema,
        schema_description.Description.description AS schema_description,
        table.Table.name AS name, id(table) AS key, table_description.Description.description AS description,
        time_stamp.`Timestamp`.`timestamp` AS last_updated_timestamp,
        column_names,
        column_descriptions,
        total_usage,
        unique_usage,
        `tags`,
        badges,
        programmatic_descriptions
        ORDER BY name;
        """)

    DEFAULT_NEBULA_USER_CYPHER_QUERY = textwrap.dedent("""
        MATCH (`user`:`User`)
        OPTIONAL MATCH (`user`)-[read:READ]->(a)
        OPTIONAL MATCH (`user`)-[own:OWNER_OF]->(b)
        OPTIONAL MATCH (`user`)-[follow:FOLLOWED_BY]->(c)
        OPTIONAL MATCH (`user`)-[manage_by:MANAGE_BY]->(manager)
        {publish_tag_filter}
        WITH `user`, a, b, c, read, own, follow, manager
        WHERE `user`.`User`.full_name IS NOT NULL
        RETURN `user`.`User`.email AS email, `user`.`User`.first_name AS first_name, `user`.`User`.last_name AS last_name,
        `user`.`User`.full_name AS full_name, `user`.`User`.github_username AS github_username, `user`.`User`.team_name AS team_name,
        `user`.`User`.employee_type AS employee_type, manager.`User`.email AS manager_email,
        `user`.`User`.slack_id AS slack_id, `user`.`User`.is_active AS is_active, `user`.`User`.role_name AS role_name,
        REDUCE(sum_r = 0, r in COLLECT(DISTINCT read)| sum_r + r.read_count) AS total_read,
        COUNT(distinct b) AS total_own,
        COUNT(distinct c) AS total_follow
        ORDER BY email
        """)

    DEFAULT_NEBULA_DASHBOARD_CYPHER_QUERY = textwrap.dedent("""
         MATCH (dashboard:Dashboard)
         {publish_tag_filter}
         MATCH (dashboard)-[:DASHBOARD_OF]->(dbg:Dashboardgroup)
         MATCH (dbg)-[:DASHBOARD_GROUP_OF]->(cluster:Cluster)
         OPTIONAL MATCH (dashboard)-[:DESCRIPTION]->(db_descr:Description)
         OPTIONAL MATCH (dbg)-[:DESCRIPTION]->(dbg_descr:Description)
         OPTIONAL MATCH (dashboard)-[:EXECUTED]->(last_exec:Execution)
         WHERE SPLIT(id(last_exec), '/')[5] == '_last_successful_execution'
         OPTIONAL MATCH (dashboard)-[read:READ_BY]->(`user`:`User`)
         WITH dashboard, dbg, db_descr, dbg_descr, cluster, last_exec, SUM(read.read_count) AS total_usage
         OPTIONAL MATCH (dashboard)-[:HAS_QUERY]->(`query`:`Query`)-[:HAS_CHART]->(chart:Chart)
         WITH dashboard, dbg, db_descr, dbg_descr, cluster, last_exec, COLLECT(DISTINCT `query`.`Query`.name) AS query_names,
         COLLECT(DISTINCT chart.Chart.name) AS chart_names,
         total_usage
         OPTIONAL MATCH (dashboard)-[:TAGGED_BY]->(`tags`:`Tag`) WHERE `tags`.`Tag`.tag_type == 'default'
         WITH dashboard, dbg, db_descr, dbg_descr, cluster, last_exec, query_names, chart_names, total_usage,
         COLLECT(DISTINCT id(`tags`)) AS `tags`
         OPTIONAL MATCH (dashboard)-[:HAS_BADGE]->(badges:Badge)
         WITH  dashboard, dbg, db_descr, dbg_descr, cluster, last_exec, query_names, chart_names, total_usage, `tags`,
         COLLECT(DISTINCT id(`badges`)) AS badges
         RETURN dbg.Dashboardgroup.name AS group_name, dashboard.Dashboard.name AS name, cluster.Cluster.name AS cluster,
         COALESCE(db_descr.Description.description, '') AS description,
         COALESCE(dbg.Dashboardgroup.description, '') AS group_description, dbg.Dashboardgroup.dashboard_group_url AS group_url,
         dashboard.Dashboard.dashboard_url AS url, id(dashboard) AS uri,
         SPLIT(id(dashboard), '_')[0] AS product, toInteger(last_exec.Execution.`timestamp`) AS last_successful_run_timestamp,
         query_names, chart_names, total_usage, `tags`, badges
         ORDER BY group_name
        """)

    DEFAULT_NEBULA_FEATURE_CYPHER_QUERY = textwrap.dedent("""
         MATCH (feature:Feature)
         {publish_tag_filter}
         OPTIONAL MATCH (fg:Feature_Group)-[:`GROUPS`]->(feature)
         OPTIONAL MATCH (db:Database)-[:AVAILABLE_FEATURE]->(feature)
         OPTIONAL MATCH (feature)-[:DESCRIPTION]->(description:Description)
         OPTIONAL MATCH (feature)-[:TAGGED_BY]->(`tag`:`Tag`)
         OPTIONAL MATCH (feature)-[:HAS_BADGE]->(badge:Badge)
         OPTIONAL MATCH (feature)-[read:READ_BY]->(`user`:`User`)
         RETURN
         fg.Feature_Group.name AS feature_group,
         feature.Feature.name AS feature_name,
         feature.Feature.version AS version,
         id(feature) AS key,
         SUM(read.read_count) AS total_usage,
         feature.Feature.status AS status,
         feature.Feature.entity AS entity,
         description.Description.description AS description,
         db.Database.name AS availability,
         COLLECT(DISTINCT id(`badge`)) AS badges,
         COLLECT(DISTINCT id(`tag`)) AS `tags`,
         toInteger(feature.Feature.`timestamp`) AS last_updated_timestamp
         ORDER BY feature_group, feature_name, version
        """)

    DEFAULT_QUERY_BY_ENTITY = {
        'table': DEFAULT_NEBULA_TABLE_CYPHER_QUERY,
        'user': DEFAULT_NEBULA_USER_CYPHER_QUERY,
        'dashboard': DEFAULT_NEBULA_DASHBOARD_CYPHER_QUERY,
        'feature': DEFAULT_NEBULA_FEATURE_CYPHER_QUERY,
    }

    TAG_NAME_BY_ENTITY = {
        'table': TableMetadata.TABLE_NODE_LABEL,
        'user': UserMetadata.USER_NODE_LABEL,
        'dashboard': DashboardMetadata.DASHBOARD_NODE_LABEL,
        'feature': FeatureMetadata.NODE_LABEL,
    }

    def init(self, conf: ConfigTree) -> None:
        """
        Initialize NebulaExtractor object from configuration and use that for extraction
        """
        self.conf = conf
        self.entity = conf.get_string(NebulaSearchDataExtractor.ENTITY_TYPE,
                                      default='table').lower()
        # extract cypher query from conf, if specified, else use default query
        if NebulaSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY in conf:
            self.cypher_query = conf.get_string(
                NebulaSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY)
        else:
            default_query = NebulaSearchDataExtractor.DEFAULT_QUERY_BY_ENTITY[
                self.entity]
            self.cypher_query = self._add_publish_tag_filter(
                conf.get_string(JOB_PUBLISH_TAG, ''),
                cypher_query=default_query)

        self.nebula_extractor = NebulaExtractor()
        # write the cypher query in configs in NebulaExtractor scope
        key = self.nebula_extractor.get_scope(
        ) + '.' + NebulaExtractor.CYPHER_QUERY_CONFIG_KEY
        self.conf.put(key, self.cypher_query)
        # initialize nebula_extractor from configs
        self.nebula_extractor.init(
            Scoped.get_scoped_conf(self.conf,
                                   self.nebula_extractor.get_scope()))

    def close(self) -> None:
        """
        Use close() method specified by nebula_extractor
        to close connection to Nebula cluster
        """
        self.nebula_extractor.close()

    def extract(self) -> Any:
        """
        Invoke extract() method defined by nebula_extractor
        """
        return self.nebula_extractor.extract()

    def get_scope(self) -> str:
        return 'extractor.search_data'

    def _add_publish_tag_filter(self, publish_tag: str,
                                cypher_query: str) -> str:
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
            publish_tag_filter = (
                f"WHERE `{self.entity}`.`{NebulaSearchDataExtractor.TAG_NAME_BY_ENTITY[self.entity]}`"
                f".published_tag == '{publish_tag}'")
        return cypher_query.format(publish_tag_filter=publish_tag_filter)
