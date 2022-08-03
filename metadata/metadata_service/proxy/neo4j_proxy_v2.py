# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import textwrap
from typing import Any, Callable, List, Tuple
import neo4j
from neo4j import GraphDatabase, Result, Transaction
from neo4j.api import SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, SECURITY_TYPE_SECURE, parse_neo4j_uri
from amundsen_common.models.table import (Application, Badge, Column,
                                          ProgrammaticDescription, Reader,
                                          ResourceReport, Source, SqlJoin,
                                          SqlWhere, Stat, Table, TableSummary,
                                          Tag, TypeMetadata, User, Watermark)
from metadata_service.exception import NotFoundException
from metadata_service.proxy.base_proxy import BaseProxy

LOGGER = logging.getLogger(__name__)


class Neo4jProxy(BaseProxy):
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

    # General Resources Metadata Functions

    # Table Metadata Functions

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

            column_badges = self._make_badges(tbl_col_neo4j_record['col_badges'])

            col_type_metadata = self._get_type_metadata(tbl_col_neo4j_record['col_type_metadata'])

            last_neo4j_record = tbl_col_neo4j_record
            col = Column(name=tbl_col_neo4j_record['col']['name'],
                         description=self._safe_get(tbl_col_neo4j_record, 'col_dscrpt', 'description'),
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
            reader = Reader(user=self._build_user_from_record(record=reader_data),
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
        badges = self._make_badges(table_records.get('badge_records'))

        table_writer, table_apps = self._create_apps(table_records['producing_apps'], table_records['consuming_apps'])

        timestamp_value = table_records['last_updated_timestamp']

        owner_record = []

        for owner in table_records.get('owner_records', []):
            owner_data = self._get_user_details(user_id=owner['email'])
            owner_record.append(self._build_user_from_record(record=owner_data))

        src = None

        if table_records['src']:
            src = Source(source_type=table_records['src']['source_type'],
                         source=table_records['src']['source'])

        prog_descriptions = self._extract_programmatic_descriptions_from_query(
            table_records.get('prog_descriptions', [])
        )

        resource_reports = self._extract_resource_reports_from_query(table_records.get('resource_reports', []))

        return wmk_results, table_writer, table_apps, timestamp_value, owner_record,\
            tags, src, badges, prog_descriptions, resource_reports

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
        pass
