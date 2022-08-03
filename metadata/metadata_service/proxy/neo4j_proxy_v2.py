# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import re
import textwrap
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple
import neo4j
from neo4j import GraphDatabase, Result, Transaction
from neo4j.api import SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, SECURITY_TYPE_SECURE, parse_neo4j_uri
from amundsen_common.entity.resource_type import ResourceType, to_resource_type
from amundsen_common.models.table import (Application, Badge, Column,
                                          ProgrammaticDescription, Reader,
                                          ResourceReport, Source, SqlJoin,
                                          SqlWhere, Stat, Table, TableSummary,
                                          Tag, TypeMetadata, User, Watermark)

from amundsen_common.models.user import User as UserEntity
from flask import current_app, has_app_context
from metadata_service import config
from metadata_service.entity.description import Description
from metadata_service.exception import NotFoundException
from metadata_service.proxy.base_proxy import BaseProxy
from metadata_service.proxy.neo4j_utils.utils import safe_get

LOGGER = logging.getLogger(__name__)


class Neo4jProxy():
    def __init__(self, *,
                 host: str,
                 port: int,
                 user: str = 'neo4j',
                 password: str = '',
                 num_conns: int = 50,
                 max_connection_lifetime_sec: int = 100,
                 encrypted: bool = False,
                 validate_ssl: bool = False,
                 database_name: str = neo4j.DEFAULT_DATABASE,
                 **kwargs: dict) -> None:
        endpoint = f'{host}:{port}'
        LOGGER.info('NEO4J endpoint: {}'.format(endpoint))

        self._database_name = database_name

        driver_args = {
            'uri': endpoint,
            'max_connection_lifetime': max_connection_lifetime_sec,
            'auth': (user, password),
            'connection_timeout': 10,
            'max_connection_pool_size': num_conns,
        }

        # if URI scheme not secure set `trust`` and `encrypted` arguments for the driver
        # https://neo4j.com/docs/api/python-driver/current/api.html#uri
        _, security_type, _ = parse_neo4j_uri(uri=endpoint)
        if security_type not in [SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, SECURITY_TYPE_SECURE]:
            trust = neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES if validate_ssl else neo4j.TRUST_ALL_CERTIFICATES
            default_security_conf = {'trust': trust, 'encrypted': encrypted}
            driver_args.update(default_security_conf)

        # TODO driver.verify_connectivity() maybe in health check
        self._driver = driver=GraphDatabase.driver(**driver_args)

    def health(self):
        pass

    # TODO in BaseProxy
    def _get_user_details(self, user_id: str, user_data: Optional[Dict] = None) -> Dict:
        """
        Helper function to help get the user details if the `USER_DETAIL_METHOD` is configured,
        else uses the user_id for both email and user_id properties.
        :param user_id: The Unique user id of a user entity
        :return: a dictionary of user details
        """
        if current_app.config.get('USER_DETAIL_METHOD'):
            user_details = app.config.get('USER_DETAIL_METHOD')(user_id)  # type: ignore
        elif user_data:
            user_details = user_data
        else:
            user_details = {'email': user_id, 'user_id': user_id}

        return user_details

    # TODO see if create functions can be moved somewhere else since they are static and relate to model creation
    def _create_badges(self, badge_list: Iterable) -> List[Badge]:
        """
        Generates a list of Badges objects

        :param badges: A list of badges of a table, column, or type_metadata
        :return: a list of Badge objects
        """
        badges = []
        for badge in badge_list:
            badges.append(Badge(badge_name=badge["key"], category=badge["category"]))
        return badges

    def _create_user(self, record: dict, manager_name: Optional[str] = None) -> UserEntity:
        """
        Builds user record from Cypher query result. Other than the one defined in amundsen_common.models.user.User,
        you could add more fields from User node into the User model by specifying keys in config.USER_OTHER_KEYS
        :param record:
        :param manager_name:
        :return:
        """
        other_key_values = {}
        if has_app_context() and current_app.config[config.USER_OTHER_KEYS]:
            for k in current_app.config[config.USER_OTHER_KEYS]:
                if k in record:
                    other_key_values[k] = record[k]

        return UserEntity(email=record['email'],
                          user_id=record.get('user_id', record['email']),
                          first_name=record.get('first_name'),
                          last_name=record.get('last_name'),
                          full_name=record.get('full_name'),
                          is_active=record.get('is_active', True),
                          profile_url=record.get('profile_url'),
                          github_username=record.get('github_username'),
                          team_name=record.get('team_name'),
                          slack_id=record.get('slack_id'),
                          employee_type=record.get('employee_type'),
                          role_name=record.get('role_name'),
                          manager_fullname=record.get('manager_fullname', manager_name),
                          other_key_values=other_key_values)

    def _create_sql_joins(self, joins: List[Dict]) -> List[SqlJoin]:
        valid_joins = []
        for join in joins:
            join_data = join['join']
            if all(join_data.values()):
                new_sql_join = SqlJoin(join_sql=join_data['join_sql'],
                                       join_type=join_data['join_type'],
                                       joined_on_column=join_data['joined_on_column'],
                                       joined_on_table=TableSummary(**join_data['joined_on_table']),
                                       column=join_data['column'])
                valid_joins.append(new_sql_join)
        return valid_joins

    def _create_sql_where(self, filters: List[Dict]) -> List[SqlWhere]:
        return_filters = []
        for filt in filters:
            filter_where = filt.get('where_clause')
            if filter_where:
                return_filters.append(SqlWhere(where_clause=filter_where))
        return return_filters

    def _create_resource_reports(self, raw_resource_reports: dict) -> list:
        resource_reports = []
        for resource_report in raw_resource_reports:
            name = resource_report.get('name')
            if name is None:
                LOGGER.error("A report with no name found... skipping.")
            else:
                resource_reports.append(ResourceReport(name=name, url=resource_report['url']))

        parsed_reports = current_app.config['RESOURCE_REPORT_CLIENT'](resource_reports) \
            if current_app.config['RESOURCE_REPORT_CLIENT'] else resource_reports

        parsed_reports.sort(key=lambda x: x.name)

        return parsed_reports

    def _create_app(self, app_record: dict, kind: str) -> Application:
        return Application(
            name=app_record['name'],
            id=app_record['id'],
            application_url=app_record['application_url'],
            description=app_record.get('description'),
            kind=kind,
        )
    def _create_apps(self,
                     producing_app_records: List,
                     consuming_app_records: List) -> Tuple[Application, List[Application]]:

        table_apps = []
        for record in producing_app_records:
            table_apps.append(self._create_app(record, kind='Producing'))

        # for bw compatibility, we populate table_writer with one of the producing apps
        table_writer = table_apps[0] if table_apps else None

        _producing_app_ids = {app.id for app in table_apps}
        for record in consuming_app_records:
            # if an app has both a consuming and producing relationship with a table
            # (e.g. an app that reads writes back to its input table), we call it a Producing app and
            # do not add it again
            if record['id'] not in _producing_app_ids:
                table_apps.append(self._create_app(record, kind='Consuming'))

        return table_writer, table_apps

    def _create_programmatic_descriptions(self, raw_prog_descriptions: dict) -> list:
        prog_descriptions = []
        for prog_description in raw_prog_descriptions:
            source = prog_description['description_source']
            if source is None:
                LOGGER.error("A programmatic description with no source was found... skipping.")
            else:
                prog_descriptions.append(ProgrammaticDescription(source=source, text=prog_description['description']))
        prog_descriptions.sort(key=lambda x: x.source)
        return prog_descriptions

    # Programmatic Descriptions Functions


    # Table Metadata Functions

    def _get_type_metadata(self, type_metadata_results: List) -> Optional[TypeMetadata]:
        """
        Generates a TypeMetadata object for a column. All columns will have at least
        one associated type metadata node if the ComplexTypeTransformer is configured
        to transform table metadata. Otherwise, there will be no type metadata found
        and this will return quickly.

        :param type_metadata_results: A list of type metadata values for a column
        :return: a TypeMetadata object
        """
        # If there are no Type_Metadata nodes, type_metadata_results will have
        # one object with an empty node value
        if len(type_metadata_results) > 0 and type_metadata_results[0]['node'] is not None:
            sorted_type_metadata = sorted(type_metadata_results, key=lambda x: x['node']['key'])
        else:
            return None

        type_metadata_nodes: Dict[str, TypeMetadata] = {}
        type_metadata_children: Dict[str, Dict] = {}
        for tm in sorted_type_metadata:
            tm_node = tm['node']
            description = safe_get(tm, 'description', 'description')
            sort_order = safe_get(tm_node, 'sort_order') or 0
            badges = safe_get(tm, 'badges')
            # kind refers to the general type of the TypeMetadata, such as "array" or "map",
            # while data_type refers to the entire type such as "array<int>" or "map<string, string>"
            type_metadata = TypeMetadata(kind=tm_node['kind'], name=tm_node['name'], key=tm_node['key'],
                                         description=description, data_type=tm_node['data_type'], sort_order=sort_order,
                                         badges=self._create_badges(badge_list=badges) if badges else [])

            # type_metadata_nodes maps each type metadata path to its corresponding TypeMetadata object
            tm_key_regex = re.compile(
                r'(?P<db>\w+):\/\/(?P<cluster>\w+)\.(?P<schema>\w+)\/(?P<tbl>\w+)\/(?P<col>\w+)\/type\/(?P<tm_path>.*)'
            )
            tm_key_match = tm_key_regex.search(type_metadata.key)
            if tm_key_match is None:
                LOGGER.error(f'Could not retrieve the type metadata path from key {type_metadata.key}')
                continue
            tm_path = tm_key_match.group('tm_path')
            type_metadata_nodes[tm_path] = type_metadata

            # type_metadata_children is a nested dict where each type metadata node name
            # maps to a dict of its children's names
            split_key_list = tm_path.split('/')
            tm_name = split_key_list.pop()
            node_children = safe_get(type_metadata_children, *split_key_list)
            if node_children is not None:
                node_children[tm_name] = {}
            else:
                LOGGER.error(f'Could not construct the dict of children for type metadata key {type_metadata.key}')

        # Iterate over the temporary children dict to create the proper TypeMetadata structure
        result = self._build_type_metadata_structure('', type_metadata_children, type_metadata_nodes)
        return result[0] if len(result) > 0 else None

    def _build_type_metadata_structure(self, prev_path: str, tm_children: Dict, tm_nodes: Dict) -> List[TypeMetadata]:
        type_metadata = []
        for node_name, children in tm_children.items():
            curr_path = f'{prev_path}/{node_name}' if prev_path else node_name
            tm = tm_nodes.get(curr_path)
            if tm is None:
                LOGGER.error(f'Could not find expected type metadata object at type metadata path {curr_path}')
                continue
            if len(children) > 0:
                tm.children = self._build_type_metadata_structure(curr_path, children, tm_nodes)
            type_metadata.append(tm)

        if len(type_metadata) > 1:
            type_metadata.sort(key=lambda x: x.sort_order)

        return type_metadata

    def _get_columns(self, tx: Transaction, table_uri: str) -> Tuple:
        """
        Execute cypher query to get all columns for a given table uri
        :return: (Columns, Last Processed Record)
        """

        column_level_query = textwrap.dedent("""
        MATCH (db:Database)-[:CLUSTER]->(clstr:Cluster)-[:SCHEMA]->(schema:Schema)
        -[:TABLE]->(tbl:Table {key: $tbl_key})-[:COLUMN]->(col:Column)
        OPTIONAL MATCH (tbl)-[:DESCRIPTION]->(tbl_dscrpt:Description)
        OPTIONAL MATCH (col:Column)-[:DESCRIPTION]->(col_dscrpt:Description)
        OPTIONAL MATCH (col:Column)-[:STAT]->(stat:Stat)
        OPTIONAL MATCH (col:Column)-[:HAS_BADGE]->(badge:Badge)
        OPTIONAL MATCH (col:Column)-[:TYPE_METADATA]->(Type_Metadata)-[:SUBTYPE *0..]->(tm:Type_Metadata)
        OPTIONAL MATCH (tm:Type_Metadata)-[:DESCRIPTION]->(tm_dscrpt:Description)
        OPTIONAL MATCH (tm:Type_Metadata)-[:HAS_BADGE]->(tm_badge:Badge)
        WITH db, clstr, schema, tbl, tbl_dscrpt, col, col_dscrpt, collect(distinct stat) as col_stats,
        collect(distinct badge) as col_badges,
        {node: tm, description: tm_dscrpt, badges: collect(distinct tm_badge)} as tm_results
        RETURN db, clstr, schema, tbl, tbl_dscrpt, col, col_dscrpt, col_stats, col_badges,
        collect(distinct tm_results) as col_type_metadata
        ORDER BY col.sort_order;""")

        cols_records = tx.run(query=column_level_query, tbl_key=table_uri)

        cols = []
        last_neo4j_record = None
        for tbl_col_neo4j_record in cols_records:
            # Getting last record from this for loop as Neo4j's result's random access is O(n) operation.
            col_stats = []
            for stat in tbl_col_neo4j_record['col_stats']:
                col_stat = Stat(
                    stat_type=stat['stat_type'],
                    stat_val=stat['stat_val'],
                    start_epoch=int(float(stat['start_epoch'])),
                    end_epoch=int(float(stat['end_epoch']))
                )
                col_stats.append(col_stat)

            column_badges = self._create_badges(badge_list=tbl_col_neo4j_record['col_badges'])

            col_type_metadata = self._get_type_metadata(tbl_col_neo4j_record['col_type_metadata'])

            last_neo4j_record = tbl_col_neo4j_record
            col = Column(name=tbl_col_neo4j_record['col']['name'],
                         description=safe_get(tbl_col_neo4j_record, 'col_dscrpt', 'description'),
                         col_type=tbl_col_neo4j_record['col']['col_type'],
                         sort_order=int(tbl_col_neo4j_record['col']['sort_order']),
                         stats=col_stats,
                         badges=column_badges,
                         type_metadata=col_type_metadata)

            cols.append(col)

        LOGGER.info(f'{cols=}')

        if not cols:
            raise NotFoundException('Table URI( {table_uri} ) does not exist'.format(table_uri=table_uri))

        return sorted(cols, key=lambda item: item.sort_order), last_neo4j_record

    def _get_table_usage(self, tx: Transaction, table_uri: str) -> List[Reader]:
        usage_query = textwrap.dedent("""\
        MATCH (user:User)-[read:READ]->(table:Table {key: $tbl_key})
        RETURN user.email as email, read.read_count as read_count, table.name as table_name
        ORDER BY read.read_count DESC LIMIT 5;
        """)

        usage_neo4j_records = tx.run(query=usage_query, tbl_key=table_uri)

        readers: List[Reader] = []
        for usage_neo4j_record in usage_neo4j_records:
            reader_data = self._get_user_details(user_id=usage_neo4j_record['email'])
            reader = Reader(user=self._create_user(record=reader_data),
                            read_count=usage_neo4j_record['read_count'])
            readers.append(reader)

        return readers

    def _get_table_extras(self, tx: Transaction, table_uri: str) -> Tuple:
        """
        Queries one Cypher record with watermark list, Application, timestamp, owners, badges, and tag records.
        :return: (Watermark Results, Table Writer, Last Updated Timestamp, owner records, tag records)
        """

        table_level_query = textwrap.dedent("""\
        MATCH (tbl:Table {key: $tbl_key})
        OPTIONAL MATCH (wmk:Watermark)-[:BELONG_TO_TABLE]->(tbl)
        OPTIONAL MATCH (app_producer:Application)-[:GENERATES]->(tbl)
        OPTIONAL MATCH (app_consumer:Application)-[:CONSUMES]->(tbl)
        OPTIONAL MATCH (tbl)-[:LAST_UPDATED_AT]->(t:Timestamp)
        OPTIONAL MATCH (owner:User)<-[:OWNER]-(tbl)
        OPTIONAL MATCH (tbl)-[:TAGGED_BY]->(tag:Tag{tag_type: $tag_normal_type})
        OPTIONAL MATCH (tbl)-[:HAS_BADGE]->(badge:Badge)
        OPTIONAL MATCH (tbl)-[:SOURCE]->(src:Source)
        OPTIONAL MATCH (tbl)-[:DESCRIPTION]->(prog_descriptions:Programmatic_Description)
        OPTIONAL MATCH (tbl)-[:HAS_REPORT]->(resource_reports:Report)
        RETURN collect(distinct wmk) as wmk_records,
        collect(distinct app_producer) as producing_apps,
        collect(distinct app_consumer) as consuming_apps,
        t.last_updated_timestamp as last_updated_timestamp,
        collect(distinct owner) as owner_records,
        collect(distinct tag) as tag_records,
        collect(distinct badge) as badge_records,
        src,
        collect(distinct prog_descriptions) as prog_descriptions,
        collect(distinct resource_reports) as resource_reports
        """)

        table_records = tx.run(query=table_level_query, tbl_key=table_uri, tag_normal_type='default').single()

        wmk_results = []
        wmk_records = table_records['wmk_records']
        for record in wmk_records:
            if record['key'] is not None:
                watermark_type = record['key'].split('/')[-2]
                wmk_result = Watermark(watermark_type=watermark_type,
                                       partition_key=record['partition_key'],
                                       partition_value=record['partition_value'],
                                       create_time=record['create_time'])
                wmk_results.append(wmk_result)

        tags = []
        if table_records.get('tag_records'):
            tag_records = table_records['tag_records']
            for record in tag_records:
                tag_result = Tag(tag_name=record['key'],
                                 tag_type=record['tag_type'])
                tags.append(tag_result)

        # this is for any badges added with BadgeAPI instead of TagAPI
        badges = self._create_badges(badge_list=table_records.get('badge_records'))

        table_writer, table_apps = self._create_apps(table_records['producing_apps'], table_records['consuming_apps'])

        timestamp_value = table_records['last_updated_timestamp']

        owner_record = []

        for owner in table_records.get('owner_records', []):
            owner_data = self._get_user_details(user_id=owner['email'])
            owner_record.append(self._create_user(record=owner_data))

        src = None

        if table_records['src']:
            src = Source(source_type=table_records['src']['source_type'],
                         source=table_records['src']['source'])

        prog_descriptions = self._create_programmatic_descriptions(
            table_records.get('prog_descriptions', [])
        )

        resource_reports = self._create_resource_reports(table_records.get('resource_reports', []))

        return wmk_results, table_writer, table_apps, timestamp_value, owner_record,\
            tags, src, badges, prog_descriptions, resource_reports

    def _get_table_query(self, tx: Transaction, table_uri: str) -> Tuple:
        """
        Queries one Cypher record with results that contain information about queries
        and entities (e.g. joins, where clauses, etc.) associated to queries that are executed
        on the table.
        """

        # Return Value: (Watermark Results, Table Writer, Last Updated Timestamp, owner records, tag records)
        table_query_level_query = textwrap.dedent("""
            MATCH (tbl:Table {key: $tbl_key})
            OPTIONAL MATCH (tbl)-[:COLUMN]->(col:Column)-[COLUMN_JOINS_WITH]->(j:Join)
            OPTIONAL MATCH (j)-[JOIN_OF_COLUMN]->(col2:Column)
            OPTIONAL MATCH (j)-[JOIN_OF_QUERY]->(jq:Query)-[:HAS_EXECUTION]->(exec:Execution)
            WITH tbl, j, col, col2,
                sum(coalesce(exec.execution_count, 0)) as join_exec_cnt
            ORDER BY join_exec_cnt desc
            LIMIT 5
            WITH tbl,
                COLLECT(DISTINCT {
                join: {
                    joined_on_table: {
                        database: case when j.left_table_key = $tbl_key
                                  then j.right_database
                                  else j.left_database
                                  end,
                        cluster: case when j.left_table_key = $tbl_key
                                 then j.right_cluster
                                 else j.left_cluster
                                 end,
                        schema: case when j.left_table_key = $tbl_key
                                then j.right_schema
                                else j.left_schema
                                end,
                        name: case when j.left_table_key = $tbl_key
                              then j.right_table
                              else j.left_table
                              end
                    },
                    joined_on_column: col2.name,
                    column: col.name,
                    join_type: j.join_type,
                    join_sql: j.join_sql
                },
                join_exec_cnt: join_exec_cnt
            }) as joins
            WITH tbl, joins
            OPTIONAL MATCH (tbl)-[:COLUMN]->(col:Column)-[USES_WHERE_CLAUSE]->(whr:Where)
            OPTIONAL MATCH (whr)-[WHERE_CLAUSE_OF]->(wq:Query)-[:HAS_EXECUTION]->(whrexec:Execution)
            WITH tbl, joins,
                whr, sum(coalesce(whrexec.execution_count, 0)) as where_exec_cnt
            ORDER BY where_exec_cnt desc
            LIMIT 5
            RETURN tbl, joins,
              COLLECT(DISTINCT {
                where_clause: whr.where_clause,
                where_exec_cnt: where_exec_cnt
              }) as filters
        """)

        table_query_records = tx.run(query=table_query_level_query,
                                     tbl_key=table_uri).single()

        joins = self._create_sql_joins(table_query_records.get('joins', [{}]))
        filters = self._create_sql_where(table_query_records.get('filters', [{}]))

        return joins, filters

    #  API METHODS
    def get_table(self, *, table_uri: str) -> Table:
        """
        Get all metadata for a given table uri
        :param table_uri: table key
        :return: Table object
        """
        with self._driver.session(database=self._database_name) as session:
            cols, last_neo4j_record = session.read_transaction(transaction_function=self._get_columns,
                                                               table_uri=table_uri)
            readers = session.read_transaction(transaction_function=self._get_table_usage,
                                               table_uri=table_uri)
            wmk_results, table_writer, table_apps, timestamp_value, owners, tags, source, badges, prog_descs, \
                resource_reports = session.read_transaction(transaction_function=self._get_table_extras,
                                                            table_uri=table_uri)
            joins, filters = session.read_transaction(transaction_function=self._get_table_query,
                                                      table_uri=table_uri)
        table = Table(database=last_neo4j_record['db']['name'],
                      cluster=last_neo4j_record['clstr']['name'],
                      schema=last_neo4j_record['schema']['name'],
                      name=last_neo4j_record['tbl']['name'],
                      tags=tags,
                      badges=badges,
                      description=safe_get(last_neo4j_record, 'tbl_dscrpt', 'description'),
                      columns=cols,
                      owners=owners,
                      table_readers=readers,
                      watermarks=wmk_results,
                      table_writer=table_writer,
                      table_apps=table_apps,
                      last_updated_timestamp=timestamp_value,
                      source=source,
                      is_view=safe_get(last_neo4j_record, 'tbl', 'is_view'),
                      programmatic_descriptions=prog_descs,
                      common_joins=joins,
                      common_filters=filters,
                      resource_reports=resource_reports
                      )
        return table

    # Descriptions

    def _get_description(self, tx: Transaction, resource_type: ResourceType, uri: str) -> Description:
        """
        Get the resource description based on the uri. Any exception will propagate back to api server.

        :param resource_type:
        :param id:
        :return:
        """

        description_query = textwrap.dedent("""
        MATCH (n:{node_label} {{key: $key}})-[:DESCRIPTION]->(d:Description)
        RETURN d.description AS description;
        """.format(node_label=resource_type.name))

        result = tx.run(query=description_query, key=uri).single()

        return Description(description=result['description'] if result else None)

    def get_resource_description(self, *, resource_type: ResourceType, uri: str) -> Union[str, None]:
        """
        Get the table description based on table uri. Any exception will propagate back to api server.

        :param table_uri:
        :return:
        """
        with self._driver.session(database=self._database_name) as session:
            return session.read_transaction(transaction_function=self._get_description, resource_type=resource_type,
                                            uri=uri).single()
