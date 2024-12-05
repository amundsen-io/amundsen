# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import textwrap

# These queries are meant to be used to extract search metadata from neo4j
# using SearchMetadatatoElasticasearchTask

NEO4J_TABLE_CYPHER_QUERY = textwrap.dedent(
    """
    MATCH (db:Database)<-[:CLUSTER_OF]-(cluster:Cluster)
    <-[:SCHEMA_OF]-(schema:Schema)<-[:TABLE_OF]-(table:Table)
    {publish_tag_filter}
    OPTIONAL MATCH (schema)-[:DESCRIPTION]->(schema_description:Description)
    OPTIONAL MATCH (table)-[:DESCRIPTION]->(table_description:Description)
    OPTIONAL MATCH (table)-[:TAGGED_BY]->(tags:Tag) WHERE tags.tag_type='default'
    WITH db, cluster, schema, schema_description, table, table_description,
    COLLECT(DISTINCT toLower(tags.key)) as tags
    OPTIONAL MATCH (table)-[:HAS_BADGE]->(badges:Badge)
    WITH db, cluster, schema, schema_description, table, table_description, tags,
    COLLECT(DISTINCT toLower(badges.key)) as badges
    MATCH (table)-[:COLUMN]->(col:Column)
    OPTIONAL MATCH (col)-[:DESCRIPTION]->(col_description:Description)
    WITH db, cluster, schema, schema_description, table, table_description, tags, badges,
    COLLECT(toLower(col.name)) AS columns, COLLECT(col_description.description) AS column_descriptions
    OPTIONAL MATCH (table)-[:LAST_UPDATED_AT]->(time_stamp:Timestamp)
    {additional_field_match}
    RETURN toLower(db.name) as database, cluster.name AS cluster, toLower(schema.name) AS schema,
    schema_description.description AS schema_description,
    toLower(table.name) AS name, table.key AS key, table_description.description AS description,
    time_stamp.last_updated_timestamp AS last_updated_timestamp,
    {{
        {usage_fields}
    }} AS usage,
    columns,
    column_descriptions,
    tags,
    {additional_field_return}
    badges
    ORDER BY table.name;
    """
)

DEFAULT_TABLE_QUERY = NEO4J_TABLE_CYPHER_QUERY.format(
    publish_tag_filter='',
    additional_field_match="""
        OPTIONAL MATCH (table)-[read:READ_BY]->(user:User)
        WITH db, cluster, schema, schema_description, table, table_description, time_stamp,
        tags, badges, columns, column_descriptions, SUM(read.read_count) AS total_usage,
        COUNT(DISTINCT user.email) AS unique_usage
    """,
    usage_fields="""
        total_usage: CASE total_usage
        WHEN 0 THEN null
        ELSE total_usage
        END,
        unique_usage: CASE unique_usage
        WHEN 0 THEN null
        ELSE unique_usage
        END
    """,
    additional_field_return='')

NEO4J_DASHBOARD_CYPHER_QUERY = textwrap.dedent(
    """
        MATCH (dashboard:Dashboard)-[:DASHBOARD_OF]->(dbg:Dashboardgroup)
        -[:DASHBOARD_GROUP_OF]->(cluster:Cluster)
        {publish_tag_filter}
        OPTIONAL MATCH (dbg)-[:DESCRIPTION]->(dbg_descr:Description)
        OPTIONAL MATCH (dashboard)-[:DESCRIPTION]->(db_descr:Description)
        OPTIONAL MATCH (dashboard)-[:EXECUTED]->(last_exec:Execution)
        WHERE split(last_exec.key, '/')[5] = '_last_successful_execution'
        OPTIONAL MATCH (dashboard)-[:HAS_QUERY]->(query:Query)-[:HAS_CHART]->(chart:Chart)
        WITH dashboard, dbg, db_descr, dbg_descr, cluster, last_exec, COLLECT(DISTINCT query.name) as query_names,
        COLLECT(DISTINCT chart.name) as chart_names
        OPTIONAL MATCH (dashboard)-[:TAGGED_BY]->(tags:Tag) WHERE tags.tag_type='default'
        WITH dashboard, dbg, db_descr, dbg_descr, cluster, last_exec, query_names, chart_names,
        COLLECT(DISTINCT toLower(tags.key)) as tags
        OPTIONAL MATCH (dashboard)-[:HAS_BADGE]->(badges:Badge)
        WITH  dashboard, dbg, db_descr, dbg_descr, cluster, last_exec, query_names, chart_names, tags,
        COLLECT(DISTINCT badges.key) as badges
        {additional_field_match}
        RETURN toLower(dbg.name) as group_name, toLower(dashboard.name) as name, cluster.name as cluster,
        {additional_field_return}
        {{
            {usage_fields}
        }} AS usage,
        coalesce(db_descr.description, '') as description,
        coalesce(dbg.description, '') as group_description, dbg.dashboard_group_url as group_url,
        dashboard.dashboard_url as url, dashboard.key as key, dashboard.key as uri,
        split(dashboard.key, '_')[0] as product, toInteger(last_exec.timestamp) as last_successful_run_timestamp,
        query_names, chart_names, tags, badges
        order by dbg.name
    """
)

DEFAULT_DASHBOARD_QUERY = NEO4J_DASHBOARD_CYPHER_QUERY.format(
    publish_tag_filter='',
    additional_field_match="""
        OPTIONAL MATCH (dashboard)-[read:READ_BY]->(user:User)
        WITH  dashboard, dbg, db_descr, dbg_descr, cluster, last_exec, query_names, chart_names, tags,
        badges, SUM(read.read_count) AS total_usage
    """,
    usage_fields="""
        total_usage: CASE total_usage
        WHEN 0 THEN null
        ELSE total_usage
        END
    """,
    additional_field_return='')

NEO4J_USER_CYPHER_QUERY = textwrap.dedent(
    """
    MATCH (user:User)
    {additional_field_match}
    OPTIONAL MATCH (user)-[read:READ]->(a)
    OPTIONAL MATCH (user)-[own:OWNER_OF]->(b)
    OPTIONAL MATCH (user)-[follow:FOLLOWED_BY]->(c)
    OPTIONAL MATCH (user)-[manage_by:MANAGE_BY]->(manager)
    {publish_tag_filter}
    with user, a, b, c, read, own, follow, manager
    where user.full_name is not null
    return user.email as key, user.first_name as first_name, user.last_name as last_name,
    {{
        {usage_fields}
    }} AS usage,
    user.full_name as name, user.github_username as github_username, user.team_name as team_name,
    user.employee_type as employee_type, manager.email as manager_email,
    {additional_field_return}
    user.slack_id as slack_id, toBoolean(user.is_active) as is_active, user.role_name as role_name
    order by user.email
    """
)

DEFAULT_USER_QUERY = NEO4J_USER_CYPHER_QUERY.format(
    publish_tag_filter='',
    additional_field_match='',
    usage_fields="""
        total_read: CASE sum(read.read_count)
        WHEN 0 THEN null
        ELSE sum(read.read_count)
        END,
        total_own: CASE count(distinct b)
        WHEN 0 THEN null
        ELSE count(distinct b)
        END,
        total_follow: CASE count(distinct c)
        WHEN 0 THEN null
        ELSE count(distinct c)
        END
    """,
    additional_field_return='')

NEO4J_FEATURE_CYPHER_QUERY = textwrap.dedent(
    """
        MATCH (feature:Feature)
        {publish_tag_filter}
        OPTIONAL MATCH (fg:Feature_Group)-[:GROUPS]->(feature)
        OPTIONAL MATCH (db:Database)-[:AVAILABLE_FEATURE]->(feature)
        OPTIONAL MATCH (feature)-[:DESCRIPTION]->(desc:Description)
        OPTIONAL MATCH (feature)-[:TAGGED_BY]->(tag:Tag)
        OPTIONAL MATCH (feature)-[:HAS_BADGE]->(badge:Badge)
        {additional_field_match}
        RETURN
        toLower(fg.name) as feature_group,
        toLower(feature.name) as name,
        feature.version as version,
        feature.key as key,
        {additional_field_return}
        {{
            {usage_fields}
        }} AS usage,
        feature.status as status,
        toLower(feature.entity) as entity,
        desc.description as description,
        db.name as availability,
        COLLECT(DISTINCT toLower(badge.key)) as badges,
        COLLECT(DISTINCT toLower(tag.key)) as tags,
        toInteger(feature.last_updated_timestamp) as last_updated_timestamp
        order by feature_group, name, version
    """
)

DEFAULT_FEATURE_QUERY = NEO4J_FEATURE_CYPHER_QUERY.format(
    publish_tag_filter='',
    additional_field_match="""
        OPTIONAL MATCH (feature)-[read:READ_BY]->(user:User)
        WITH feature, fg, db, desc, tag, badge, SUM(read.read_count) as total_usage
    """,
    usage_fields="""
        total_usage: CASE total_usage
        WHEN 0 THEN null
        ELSE total_usage
        END
        """,
    additional_field_return='')
