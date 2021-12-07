# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import queue
import re
import textwrap
import time

from threading import Lock, Timer

from contextlib import contextmanager
from random import randint
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,  # noqa: F401
    Union,
    no_type_check)

from amundsen_common.entity.resource_type import ResourceType, to_resource_type
from amundsen_common.models.api import health_check
from amundsen_common.models.dashboard import DashboardSummary
from amundsen_common.models.feature import Feature, FeatureWatermark
from amundsen_common.models.generation_code import GenerationCode
from amundsen_common.models.lineage import Lineage, LineageItem
from amundsen_common.models.popular_table import PopularTable
from amundsen_common.models.table import (Application, Badge, Column,
                                          ProgrammaticDescription, Reader,
                                          ResourceReport, Source, SqlJoin,
                                          SqlWhere, Stat, Table, TableSummary,
                                          Tag, TypeMetadata, User, Watermark)
from amundsen_common.models.user import User as UserEntity
from amundsen_common.models.user import UserSchema
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from flask import current_app, has_app_context
from jinja2 import Template
from nebula3.Config import Config as NebulaConfig
from nebula3.gclient.net import ConnectionPool, Session
from nebula3.fbthrift.transport.TTransport import TTransportException
from nebula3.Exception import IOErrorException, NotValidConnectionException
from metadata_service import config
from metadata_service.entity.dashboard_detail import \
    DashboardDetail as DashboardDetailEntity
from metadata_service.entity.dashboard_query import \
    DashboardQuery as DashboardQueryEntity
from metadata_service.entity.description import Description
from metadata_service.entity.tag_detail import TagDetail
from metadata_service.exception import NotFoundException
from metadata_service.proxy.base_proxy import BaseProxy
from metadata_service.proxy.statsd_utilities import timer_with_counter
from metadata_service.util import UserResourceRel

_CACHE = CacheManager(**parse_cache_config_options({'cache.type': 'memory'}))

# Expire cache every 11 hours + jitter
_GET_POPULAR_RESOURCES_CACHE_EXPIRY_SEC = 11 * 60 * 60 + randint(0, 3600)

CREATED_EPOCH_MS = 'publisher_created_epoch_ms'
LAST_UPDATED_EPOCH_MS = 'publisher_last_updated_epoch_ms'
PUBLISHED_PROPERTY_NAME = 'published_tag'

CONN_INIT_LOCK_TIMEOUT = 10

LOGGER = logging.getLogger(__name__)

_NEBULA_CONNECTION_INIT_LOCK = Lock()


class NebulaQueryExecutionError(Exception):

    def __init__(self, code, errors):
        self.code = code
        self.errors = errors

    def __str__(self):
        return "Nebula Query Execution Error: " + str(self.code) + ", " + str(
            self.errors)


class NebulaProxy(BaseProxy):
    """
    A proxy to Nebula (Gateway to Nebula)
    """

    def __init__(self,
                 *,
                 host: str,
                 port: int,
                 user: str,
                 password: str,
                 num_conns: int = 100,
                 query_timeout_sec: int = 100,
                 space: str = "amundsen",
                 **kwargs: dict) -> None:
        """
        By default, it will set max number of connections to 100 and connection time out to 100 seconds.
        :param num_conns: number of connections
        :param query_timeout_sec: Maximu query shoot waiting timer. This value needs to be smaller
        than surrounding network environment's timeout.
        ToDo: TLS support.
        """
        LOGGER.info(
            f"Nebula Proxy init with hosts: {host}, port: {port}"
            f", num_conns: {num_conns}, query_timeout_sec: {query_timeout_sec}"
        )
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.config = NebulaConfig()
        self.config.max_connection_pool_size = num_conns
        self.config.timeout = query_timeout_sec * 1000
        self.space = space
        self._queue = None
        self._connection_pool = None
        self.init_connection()

    def init_connection(self) -> None:
        hosts = self.host.split(",")
        with self.get_conn_init_lock(timeout_sec=3,
                                     delay_sec=CONN_INIT_LOCK_TIMEOUT) as lock:
            if not lock:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug("Failed to acquire lock to init connection,"
                                 " skipping init...(this should be fine as "
                                 "another connection init should be ongoing.)")
                return
            _queue = queue.Queue()
            if self._connection_pool is not None:
                LOGGER.info(
                    "Connection pool already exists, this is a reconnection attempt, "
                    "closing the old pool first.")
                self._connection_pool.close()
            self._connection_pool = ConnectionPool()
            self._connection_pool.init([(h, self.port) for h in hosts],
                                       self.config)

            r_error = []
            for c in range(self.config.max_connection_pool_size):
                session = self._connection_pool.get_session(
                    self.user, self.password)
                result = session.execute_json(f"USE { self.space }")
                r_, r_code = self._decode_json_result(result)
                if r_code != 0:
                    r_error.append(r_)
                    if LOGGER.isEnabledFor(logging.DEBUG):
                        LOGGER.exception(
                            f"Switching Space: { self.space } failed "
                            f"with code: { r_code }, hosts: { hosts }, "
                            f"please ensure the Nebula Graph was"
                            f"bootstraped with Dataloader. Result: { r_ }")
                else:
                    _queue.put(session)
            if 0 < _queue.qsize() < self.config.max_connection_pool_size:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug(
                        f"Failure occurred during to init connection pool, only { _queue.qsize() } connections"
                        f"are available, expected { self.config.max_connection_pool_size } connections."
                    )
            if _queue.qsize() == 0:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug(
                        f"Failed to init connection pool, no connection got, "
                        f"hosts: { hosts }, please ensure the Nebula Graph cluster"
                        f"is ready. Results: { r_error }")
                raise NebulaQueryExecutionError(
                    "", f"Failed to init connection pool, no connection got"
                    f"hosts: { hosts }, please ensure the Nebula Graph cluster"
                    f"is ready. First failure result: { r_error[:1] }")

            if self._queue:
                old_queue = self._queue
                self._queue = _queue
                for s in old_queue.queue:
                    s.release()
            else:
                self._queue = _queue

    @contextmanager
    def get_conn_init_lock(self,
                           timeout_sec: int,
                           delay_sec: int = 10) -> bool:
        """
        Acquire the lock to init the connection pool.
        :param timeout_sec: timeout in seconds
        :param delay_sec: delay in seconds, this was used to avoid race condition
        """
        lock = False
        try:
            lock = _NEBULA_CONNECTION_INIT_LOCK.acquire(timeout=timeout_sec)
            yield lock

        except Exception as e:
            if LOGGER.isEnabledFor(logging.DEBUG):
                LOGGER.exception(
                    f"Something went wrong during the connection init: { e }")
        finally:
            if lock and _NEBULA_CONNECTION_INIT_LOCK.locked():
                LOGGER.info(f"Will release lock in { delay_sec } seconds"
                            f" to avoid race condtion.")
                try:
                    delay_timer = Timer(delay_sec,
                                        _NEBULA_CONNECTION_INIT_LOCK.release)
                    delay_timer.start()
                except RuntimeError:
                    pass
                except Exception as e:
                    if LOGGER.isEnabledFor(logging.DEBUG):
                        LOGGER.exception(f"Force release lock failed: { e },")

    @contextmanager
    def get_session(self) -> Session:
        try:
            if self._queue is None:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug(
                        "Connection pool was not initialized, init it.")
                self.init_connection()
            session = self._queue.get(timeout=1)
            queue_id = id(self._queue)
        except queue.Empty:
            queue_size = self._queue.qsize()
            if queue_size < self.config.max_connection_pool_size:
                try:
                    session = self._connection_pool.get_session(
                        self.user, self.password)
                    session.execute_json(f"USE { self.space }")
                except Exception as e:
                    if LOGGER.isEnabledFor(logging.DEBUG):
                        LOGGER.debug(f"Failed to get a new session: { e }"
                                     f"when queue size is { queue_size }")
                    raise NebulaQueryExecutionError(
                        "", f"Failed to get session: { e }")
            else:
                raise NebulaQueryExecutionError(
                    "", f"maximum connection pool size reached")

        try:
            yield session

        except (TTransportException, IOErrorException, RuntimeError,
                NotValidConnectionException) as e:
            # idle session will be released from server side
            # see: https://docs.nebula-graph.io/3.0.2/5.configurations-and-logs/1.configurations/3.graph-config/
            # client_idle_timeout_secs and session_idle_timeout_secs to be configured in graphd.conf
            LOGGER.exception(
                f"Connection to Nebula Graph is lost. It could be "
                f"due to idle for too long or network issue: { e }. "
                f"Trying to reconnect...")
            self.init_connection()
            raise e

        finally:
            try:
                if session:
                    if id(self._queue) == queue_id:
                        if not session.ping():
                            if LOGGER.isEnabledFor(logging.DEBUG):
                                LOGGER.debug(
                                    f"Session { session } is not valid anymore, "
                                    f"will release it.")
                            session.release()
                            del session
                        self._queue.put(session)
                    else:
                        # self._queue was muted, we won't put it back to queue
                        if LOGGER.isEnabledFor(logging.DEBUG):
                            LOGGER.debug(
                                f"Queue { self._queue } was muted, will not put "
                                f"back session: { session }, "
                                f"queue size: { self._queue.qsize() }")
                        session.release()
                        del session
            except NameError:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug(
                        "session was deleted, will not be put back to queue")
            except Exception as e:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.exception(
                        f"Failed to put session back to queue: { e }")

    def health(self) -> health_check.HealthCheck:
        """
        Check storaged hosts status.
        ToDo: Check partitions status.
        :return:
        """
        try:
            cluster_overview = self._execute_query(query='SHOW HOSTS;',
                                                   param_dict={})[0]
            i_status = self._get_result_column_index(cluster_overview,
                                                     'Status')
            status = health_check.OK
            for host in cluster_overview['data']:
                if host['row'][i_status] != "ONLINE":
                    status = health_check.FAIL
            if not cluster_overview['data']:
                status = health_check.FAIL

        except Exception as e:
            status = health_check.FAIL
            if LOGGER.isEnabledFor(logging.DEBUG):
                LOGGER.exception("Error while executing health check, %s", e)
        return health_check.HealthCheck(status=status, checks={})

    @staticmethod
    def _get_result_column(query_result, column_name):
        """
        Get the value of a column from a query result.
        """
        if "columns" not in query_result:
            raise ValueError("Query result does not have columns")

        if column_name not in query_result.get("columns", []):
            raise ValueError(
                "Query result does not have column {}".format(column_name))

        column_index = query_result["columns"].index(column_name)

        meta, data = list(), list()
        for cursor in range(len(query_result["data"])):
            d = query_result["data"][cursor]
            meta.append(d["meta"][column_index])
            data.append(d["row"][column_index])
        return data, meta

    @staticmethod
    def _get_result_record_count(query_result):
        """
        Get the count of records from a query result.
        """
        if "data" not in query_result:
            raise ValueError("Query result does not have data")

        return len(query_result["data"])

    @staticmethod
    def _get_result_column_index(query_result, column_name):
        """
        Get the count of records from a query result.
        """
        if "columns" not in query_result:
            raise ValueError("Query result does not have data")

        return query_result["columns"].index(column_name)

    @staticmethod
    def _get_result_column_indexes(query_result: dict,
                                   column_names: List[str]):
        """
        Get the indexes of columns from a query result.
        """
        if "columns" not in query_result:
            raise ValueError("Query result does not have data")

        return [
            query_result["columns"].index(column_name)
            for column_name in column_names
        ]

    @staticmethod
    def _format_record(record: dict, tag_name: str) -> None:
        """
        Format a record from a query result to remove Nebula Graph Tag
        from the property name
        """
        if not record:
            return
        del_keys = []
        for key, value in record.items():
            if key.startswith(f"{ tag_name }."):
                del_keys.append(key)
                new_key = key.replace(f"{ tag_name }.", "")
                if new_key in record:
                    if record[new_key] != value:
                        raise ValueError(
                            f"Conflict: { key } and { new_key } in { record }")
        for key in del_keys:
            new_key = key.replace(f"{ tag_name }.", "")
            record[new_key] = record[key]
            del record[key]

    @timer_with_counter
    def get_table(self, *, table_uri: str) -> Table:
        """
        :param table_uri: Table URI
        :return:  A Table object
        """

        cols, table_last = self._exec_col_query(table_uri)

        readers = self._exec_usage_query(table_uri)

        wmk_results, table_writer, table_apps, timestamp_value, owners, tags, source, \
            badges, prog_descs, resource_reports = self._exec_table_query(table_uri)

        joins, filters = self._exec_table_query_query(table_uri)

        table = Table(
            database=table_last[0]['Database.name'],
            cluster=table_last[1]['Cluster.name'],
            schema=table_last[2]['Schema.name'],
            name=table_last[3]['Table.name'],
            tags=tags,
            badges=badges,
            description=table_last[4].get('Description.description', None)
            if table_last[4] else None,
            columns=cols,
            owners=owners,
            table_readers=readers,
            watermarks=wmk_results,
            table_writer=table_writer,
            table_apps=table_apps,
            last_updated_timestamp=timestamp_value,
            source=source,
            is_view=table_last[3].get('Table.is_view', None),
            programmatic_descriptions=prog_descs,
            common_joins=joins,
            common_filters=filters,
            resource_reports=resource_reports)

        return table

    @timer_with_counter
    def _exec_col_query(self, table_uri: str) -> Tuple:
        # Return Value: (Columns, Last Row of Query)
        # Note: collect(distinct tm_badge) AS tm_badges was handled in yet another
        # layer of WITH in Nebula Graph
        column_level_query = Template(
            textwrap.dedent("""
        MATCH (db:Database)-[:CLUSTER]->(clstr:Cluster)-[:SCHEMA]->(schema:Schema)
        -[:TABLE]->(tbl:Table)-[:COLUMN]->(col:Column)
        WHERE id(tbl) == "{{ vid }}"
        OPTIONAL MATCH (tbl)-[:DESCRIPTION]->(tbl_dscrpt:Description)
        OPTIONAL MATCH (col:Column)-[:DESCRIPTION]->(col_dscrpt:Description)
        OPTIONAL MATCH (col:Column)-[:STAT]->(stat:Stat)
        OPTIONAL MATCH (col:Column)-[:HAS_BADGE]->(badge:Badge)
        OPTIONAL MATCH (col:Column)-[:TYPE_METADATA]->(Type_Metadata)-[:SUBTYPE *0..]->(tm:Type_Metadata)
        OPTIONAL MATCH (tm:Type_Metadata)-[:DESCRIPTION]->(tm_dscrpt:Description)
        OPTIONAL MATCH (tm:Type_Metadata)-[:HAS_BADGE]->(tm_badge:Badge)
        WITH db, clstr, schema, tbl, tbl_dscrpt, col, col_dscrpt, collect(distinct stat) AS col_stats,
        collect(distinct badge) AS col_badges, col.Column.sort_order AS sort_order,
        {node: tm, description: tm_dscrpt} AS tm_results, collect(distinct tm_badge) AS tm_badges
        RETURN db, clstr, schema, tbl, tbl_dscrpt, col, col_dscrpt, col_stats, col_badges,
        collect(distinct {node: tm_results['node'], description: tm_results['description'], badge: tm_badges}) AS col_type_metadata,
        sort_order ORDER BY sort_order;"""))

        tbl_col_nebula_records = self._execute_query(
            query=column_level_query.render(vid=table_uri), param_dict={})[0]
        cols = []

        (i_col_stats, i_col_badges, i_col, i_col_dscrpt,
         i_col_type_metadata) = self._get_result_column_indexes(
             tbl_col_nebula_records, ('col_stats', 'col_badges', 'col',
                                      'col_dscrpt', 'col_type_metadata'))

        for record in tbl_col_nebula_records.get('data', []):
            col_stats = []
            for stat in record['row'][i_col_stats]:
                col_stat = Stat(stat_type=stat['Stat.stat_type'],
                                stat_val=stat['Stat.stat_val'],
                                start_epoch=int(float(
                                    stat['Stat.start_epoch'])),
                                end_epoch=int(float(stat['Stat.end_epoch'])))
                col_stats.append(col_stat)

            column_badges = self._make_badges(record['row'][i_col_badges],
                                              record['meta'][i_col_badges])

            col_type_metadata = self._get_type_metadata(
                record['row'][i_col_type_metadata],
                record['meta'][i_col_type_metadata])

            col = Column(name=record['row'][i_col]['Column.name'],
                         description=record['row'][i_col_dscrpt].get(
                             'Description.description', None)
                         if record['row'][i_col_dscrpt] else None,
                         col_type=record['row'][i_col]['Column.col_type'],
                         sort_order=int(
                             record['row'][i_col]['Column.sort_order']),
                         stats=col_stats,
                         badges=column_badges,
                         type_metadata=col_type_metadata)

            cols.append(col)

        if not cols:
            raise NotFoundException(
                f'Table URI( { table_uri } ) does not exist')
        table = record['row']

        return sorted(cols, key=lambda item: item.sort_order), table

    def _get_type_metadata(self, type_metadata_results: List,
                           type_metadata_meta: List) -> Optional[TypeMetadata]:
        """
        Generates a TypeMetadata object for a column. All columns will have at least
        one associated type metadata node if the ComplexTypeTransformer is configured
        to transform table metadata. Otherwise, there will be no type metadata found
        and this will return quickly.

        :param type_metadata_results: A list of type metadata values for a column
        :param type_metadata_meta: A list of type metadata meta for a column
        :return: a TypeMetadata object
        """
        # If there are no Type_Metadata nodes, type_metadata_results will have
        # one object with an empty node value

        if len(type_metadata_results
               ) > 0 and type_metadata_results[0]['node'] is not None:
            i_badge_meta, i_desc_meta, i_node_meta = 0, 1, 2
            for i, result in enumerate(type_metadata_results):
                result_meta = type_metadata_meta[i]
                for j, badge in enumerate(
                        result['badge']) if result['badge'] else []:
                    self._format_record(badge, "Badge")
                    badge['key'] = result_meta[i_badge_meta][j].get(
                        'id', None) if result_meta[i_badge_meta][j] else None

                if result['description']:
                    self._format_record(result['description'], "Description")
                    result[
                        'description']['key'] = result_meta[i_desc_meta].get(
                            'id', None) if result_meta[i_desc_meta] else None

                if result['node']:
                    self._format_record(result['node'],
                                        ResourceType.Type_Metadata.name)
                    result['node']['key'] = result_meta[i_node_meta].get(
                        'id', None) if result_meta[i_node_meta] else None
            sorted_type_metadata = sorted(type_metadata_results,
                                          key=lambda x: x['node']['key'])
        else:
            return None

        type_metadata_nodes: Dict[str, TypeMetadata] = {}
        type_metadata_children: Dict[str, Dict] = {}
        for tm in sorted_type_metadata:
            tm_node = tm['node']
            description = self._safe_get(tm, 'description', 'description')
            sort_order = self._safe_get(tm_node, 'sort_order') or 0
            badges = self._safe_get(tm, 'badges')
            # kind refers to the general type of the TypeMetadata, such as "array" or "map",
            # while data_type refers to the entire type such as "array<int>" or "map<string, string>"
            type_metadata = TypeMetadata(
                kind=tm_node['kind'],
                name=tm_node['name'],
                key=tm_node['key'],
                description=description,
                data_type=tm_node['data_type'],
                sort_order=sort_order,
                badges=self._make_badges(badges) if badges else [])

            # type_metadata_nodes maps each type metadata path to its corresponding TypeMetadata object
            tm_key_regex = re.compile(
                r'(?P<db>\w+):\/\/(?P<cluster>\w+)\.(?P<schema>\w+)\/(?P<tbl>\w+)\/(?P<col>\w+)\/type\/(?P<tm_path>.*)'
            )
            tm_key_match = tm_key_regex.search(type_metadata.key)
            if tm_key_match is None:
                LOGGER.error(
                    f'Could not retrieve the type metadata path from key {type_metadata.key}'
                )
                continue
            tm_path = tm_key_match.group('tm_path')
            type_metadata_nodes[tm_path] = type_metadata

            # type_metadata_children is a nested dict where each type metadata node name
            # maps to a dict of its children's names
            split_key_list = tm_path.split('/')
            tm_name = split_key_list.pop()
            node_children = self._safe_get(type_metadata_children,
                                           *split_key_list)
            if node_children is not None:
                node_children[tm_name] = {}
            else:
                LOGGER.error(
                    f'Could not construct the dict of children for type metadata key {type_metadata.key}'
                )

        # Iterate over the temporary children dict to create the proper TypeMetadata structure
        result = self._build_type_metadata_structure('',
                                                     type_metadata_children,
                                                     type_metadata_nodes)
        return result[0] if len(result) > 0 else None

    def _build_type_metadata_structure(self, prev_path: str, tm_children: Dict,
                                       tm_nodes: Dict) -> List[TypeMetadata]:
        type_metadata = []
        for node_name, children in tm_children.items():
            curr_path = f'{prev_path}/{node_name}' if prev_path else node_name
            tm = tm_nodes.get(curr_path)
            if tm is None:
                LOGGER.error(
                    f'Could not find expected type metadata object at type metadata path {curr_path}'
                )
                continue
            if len(children) > 0:
                tm.children = self._build_type_metadata_structure(
                    curr_path, children, tm_nodes)
            type_metadata.append(tm)

        if len(type_metadata) > 1:
            type_metadata.sort(key=lambda x: x.sort_order)

        return type_metadata

    @timer_with_counter
    def _exec_usage_query(self, table_uri: str) -> List[Reader]:
        # Return Value: List[Reader]

        usage_query = Template(
            textwrap.dedent("""
        MATCH (`user`:`User`)-[read:READ]->(table:Table)
        WHERE id(table)=="{{ vid }}"
        RETURN user.`User`.email AS email, read.read_count AS read_count, table.Table.name AS table_name
        ORDER BY read_count DESC LIMIT 5;
        """))

        usage_nebula_records = self._execute_query(
            query=usage_query.render(vid=table_uri), param_dict={})[0]
        readers = []  # type: List[Reader]

        (i_email, i_read_count) = self._get_result_column_indexes(
            usage_nebula_records, ('email', 'read_count'))

        for usage_nebula_record in usage_nebula_records.get('data', []):
            reader_data = self._get_user_details(
                user_id=usage_nebula_record['row'][i_email])
            reader = Reader(
                user=self._build_user_from_record(record=reader_data),
                read_count=usage_nebula_record['row'][i_read_count])
            readers.append(reader)

        return readers

    @timer_with_counter
    def _exec_table_query(self, table_uri: str) -> Tuple:
        """
        Queries one record with watermark list, Application,
        ,timestamp, owner records and tag records.
        """

        # Return Value: (Watermark Results, Table Writer, Last Updated Timestamp, owner records, tag records)

        # note: Use `Timestamp`.`timestamp` instead of the DEPRECATED last_updated_timestamp

        table_level_query = Template(
            textwrap.dedent("""
        MATCH (tbl:Table)
        WHERE id(tbl) == "{{ vid }}"
        OPTIONAL MATCH (wmk:Watermark)-[:BELONG_TO_TABLE]->(tbl)
        OPTIONAL MATCH (app_producer:Application)-[:GENERATES]->(tbl)
        OPTIONAL MATCH (app_consumer:Application)-[:CONSUMES]->(tbl)
        OPTIONAL MATCH (tbl)-[:LAST_UPDATED_AT]->(t:`Timestamp`)
        OPTIONAL MATCH (owner:`User`)<-[:OWNER]-(tbl)
        OPTIONAL MATCH (tbl)-[:TAGGED_BY]->(`tag`:`Tag`{tag_type: "default"})
        OPTIONAL MATCH (tbl)-[:HAS_BADGE]->(badge:Badge)
        OPTIONAL MATCH (tbl)-[:SOURCE]->(src:Source)
        OPTIONAL MATCH (tbl)-[:DESCRIPTION]->(prog_descriptions:Programmatic_Description)
        OPTIONAL MATCH (tbl)-[:HAS_REPORT]->(resource_reports:Report)
        RETURN collect(distinct wmk) AS wmk_records,
        collect(distinct app_producer) AS producing_apps,
        collect(distinct app_consumer) AS consuming_apps,
        t.`Timestamp`.`timestamp` AS last_updated_timestamp,
        collect(distinct owner) AS owner_records,
        collect(distinct `tag`) AS tag_records,
        collect(distinct badge) AS badge_records,
        src,
        collect(distinct prog_descriptions) AS prog_descriptions,
        collect(distinct resource_reports) AS resource_reports
        """))

        table_records = self._execute_query(
            query=table_level_query.render(vid=table_uri), param_dict={})[0]
        # hardcoded as default for now
        # from nebula3.common.ttypes import Value as NebulaValue
        # param_dict={"tag_normal_type": NebulaValue(sVal="default")})[0]

        (wmk_results, table_writer, table_apps, timestamp_value, owner_record,
         tags, src, badges, prog_descriptions,
         resource_reports) = ([], [], [], [], [], [], None, [], [], [])

        table_record = table_records.get('data', [])
        if not table_record:
            return (wmk_results, table_writer, table_apps, timestamp_value,
                    owner_record, tags, src, badges, prog_descriptions,
                    resource_reports)

        (i_wmk_records, i_producing_apps, i_consuming_apps,
         i_last_updated_timestamp) = self._get_result_column_indexes(
             table_records, ('wmk_records', 'producing_apps', 'consuming_apps',
                             'last_updated_timestamp'))
        (i_owner_records, i_tag_records, i_badge_records, i_src,
         i_prog_descriptions,
         i_resource_reports) = self._get_result_column_indexes(
             table_records, ('owner_records', 'tag_records', 'badge_records',
                             'src', 'prog_descriptions', 'resource_reports'))

        record = table_record[0]['row']
        meta = table_record[0]['meta']

        wmk_records, wmk_meta = record[i_wmk_records], meta[i_wmk_records]
        producing_apps, producing_apps_meta = record[i_producing_apps], meta[
            i_producing_apps]
        consuming_apps, consuming_apps_meta = record[i_consuming_apps], meta[
            i_consuming_apps]
        last_updated_timestamp = record[i_last_updated_timestamp]
        owner_records = record[i_owner_records]
        tag_records, tag_meta = record[i_tag_records], meta[i_tag_records]
        badge_records, badge_meta = record[i_badge_records], meta[
            i_badge_records]
        src_record = record[i_src]
        prog_description_records = record[i_prog_descriptions]
        resource_report_records = record[i_resource_reports]

        for wmk_i, wmk_record in enumerate(wmk_records):
            if wmk_meta[wmk_i] and wmk_meta[wmk_i].get("id", None):
                watermark_type = wmk_meta[wmk_i]['id'].split('/')[-2]
                wmk_result = Watermark(
                    watermark_type=watermark_type,
                    partition_key=wmk_record['Watermark.partition_key'],
                    partition_value=wmk_record['Watermark.partition_value'],
                    create_time=wmk_record['Watermark.create_time'])
                wmk_results.append(wmk_result)

        for tag_i, tag_record in enumerate(tag_records):
            if tag_meta[tag_i] and tag_meta[tag_i].get("id", None):
                tag_result = Tag(tag_name=tag_meta[tag_i]['id'],
                                 tag_type=tag_record['Tag.tag_type'])
                tags.append(tag_result)

        # this is for any badges added with BadgeAPI instead of TagAPI
        badges = self._make_badges(badge_records, badge_meta)

        table_writer, table_apps = self._create_apps(
            (producing_apps, producing_apps_meta),
            (consuming_apps, consuming_apps_meta))

        timestamp_value = last_updated_timestamp

        owner_record = []

        for owner in owner_records:
            owner_data = self._get_user_details(user_id=owner['User.email'])
            self._format_record(owner_data, ResourceType.User.name)
            owner_record.append(
                self._build_user_from_record(record=owner_data))

        if src_record:
            src = Source(source_type=src_record['Source.source_type'],
                         source=src_record['Source.source'])

        prog_descriptions = self._extract_programmatic_descriptions_from_query(
            prog_description_records)

        resource_reports = self._extract_resource_reports_from_query(
            resource_report_records)

        return (wmk_results, table_writer, table_apps, timestamp_value,
                owner_record, tags, src, badges, prog_descriptions,
                resource_reports)

    @timer_with_counter
    def _exec_table_query_query(self, table_uri: str) -> Tuple:
        """
        Queries one record with results that contain information about queries
        and entities (e.g. joins, where clauses, etc.) associated to queries that are executed
        on the table.
        """

        # Return Value: (Watermark Results, Table Writer, Last Updated Timestamp, owner records, tag records)
        table_query_level_query = Template(
            textwrap.dedent("""
        MATCH (tbl:Table)
        WHERE id(tbl) == "{{ vid }}"
        OPTIONAL MATCH (tbl)-[:COLUMN]->(col:Column)-[COLUMN_JOINS_WITH]->(j:Join)
        OPTIONAL MATCH (j)-[JOIN_OF_COLUMN]->(col2:Column)
        OPTIONAL MATCH (j)-[JOIN_OF_QUERY]->(jq:`Query`)-[:HAS_EXECUTION]->(exec:Execution)
        WITH tbl, j, col, col2,
            sum(coalesce(exec.Execution.execution_count, 0)) AS join_exec_cnt
        ORDER BY join_exec_cnt desc
        LIMIT 5
        WITH tbl,
            COLLECT(DISTINCT {
            join: {
                joined_on_table: {
                    database: case when j.Join.left_table_key == id(tbl)
                              then j.Join.right_database
                              else j.Join.left_database
                              end,
                    cluster: case when j.Join.left_table_key == id(tbl)
                             then j.Join.right_cluster
                             else j.Join.left_cluster
                             end,
                    schema: case when j.Join.left_table_key == id(tbl)
                            then j.Join.right_schema
                            else j.Join.left_schema
                            end,
                    name: case when j.Join.left_table_key == id(tbl)
                          then j.Join.right_table
                          else j.Join.left_table
                          end
                },
                joined_on_column: col2.Column.name,
                column: col.Column.name,
                join_type: j.Join.join_type,
                join_sql: j.Join.join_sql
            },
            join_exec_cnt: join_exec_cnt
        }) AS joins
        WITH tbl, joins
        OPTIONAL MATCH (tbl)-[:COLUMN]->(col:Column)-[USES_WHERE_CLAUSE]->(whr:`Where`)
        OPTIONAL MATCH (whr)-[WHERE_CLAUSE_OF]->(wq:`Query`)-[:HAS_EXECUTION]->(whrexec:Execution)
        WITH tbl, joins,
            whr, sum(coalesce(whrexec.Execution.execution_count, 0)) AS where_exec_cnt
        ORDER BY where_exec_cnt desc
        LIMIT 5
        RETURN tbl, joins,
          COLLECT(DISTINCT {
            where_clause: whr.`Where`.where_clause,
            where_exec_cnt: where_exec_cnt
          }) AS filters
        """))

        query_records = self._execute_query(
            query=table_query_level_query.render(vid=table_uri), param_dict={})

        table_query_records = query_records[0]
        joins_, _ = self._get_result_column(table_query_records, "joins")
        filters_, _ = self._get_result_column(table_query_records, "filters")

        joins = self._extract_joins_from_query(joins_[0] if joins_ else [])
        filters = self._extract_filters_from_query(
            filters_[0] if filters_ else [])

        return joins, filters

    def _extract_programmatic_descriptions_from_query(
            self, raw_prog_descriptions: dict) -> list:
        prog_descriptions = []
        for prog_description in raw_prog_descriptions:
            source = prog_description[
                'Programmatic_Description.description_source']
            if source is None:
                LOGGER.error(
                    "A programmatic description with no source was found... skipping."
                )
            else:
                prog_descriptions.append(
                    ProgrammaticDescription(
                        source=source,
                        text=prog_description[
                            'Programmatic_Description.description']))
        prog_descriptions.sort(key=lambda x: x.source)
        return prog_descriptions

    def _extract_resource_reports_from_query(
            self, raw_resource_reports: dict) -> list:
        resource_reports = []
        for resource_report in raw_resource_reports:
            name = resource_report.get('Report.name')
            if name is None:
                LOGGER.error("A report with no name found... skipping.")
            else:
                resource_reports.append(
                    ResourceReport(name=name,
                                   url=resource_report['Report.url']))

        resource_reports.sort(key=lambda x: x.name)
        return resource_reports

    def _extract_joins_from_query(self, joins: List[Dict]) -> List[Dict]:
        valid_joins = []
        for join in joins:
            join_data = join['join']
            if all(join_data.values()):
                new_sql_join = SqlJoin(
                    join_sql=join_data['join_sql'],
                    join_type=join_data['join_type'],
                    joined_on_column=join_data['joined_on_column'],
                    joined_on_table=TableSummary(
                        **join_data['joined_on_table']),
                    column=join_data['column'])
                valid_joins.append(new_sql_join)
        return valid_joins

    def _extract_filters_from_query(self, filters: List[Dict]) -> List[Dict]:
        return_filters = []
        for filt in filters:
            filter_where = filt.get('where_clause')
            if filter_where:
                return_filters.append(SqlWhere(where_clause=filter_where))
        return return_filters

    @no_type_check
    def _safe_get(self, dct, *keys):
        """
        Helper method for getting value from nested dict. This also works either key does not exist or value is None.
        :param dct:
        :param keys:
        :return:
        """
        for key in keys:
            dct = dct.get(key)
            if dct is None:
                return None
        return dct

    @staticmethod
    def _decode_json_result(raw_data: bytes) -> List:
        """
        Decode the raw bytes data into a list of dicts.
        :param raw_data:
        :return:
        """
        result_dict = json.loads(raw_data)
        return result_dict.get('results',
                               []), result_dict.get('errors',
                                                    [{}])[0].get('code', -1)

    @timer_with_counter
    def _execute_query(self, query: str, param_dict: Dict[str, Any]) -> List:
        """
        :param query:
        :param param_dict:
        :return:
        """
        with self.get_session() as session:
            try:
                r = session.execute_json_with_parameter(query, param_dict)
                results, r_code = self._decode_json_result(r)
                if r_code != 0:
                    if LOGGER.isEnabledFor(logging.DEBUG):
                        errors = results[0].get('errors', '')
                        LOGGER.debug(
                            "Failed executing query: %s, errors: %s, results: %s",
                            query, errors, results[0])
                    raise NebulaQueryExecutionError(
                        r_code, results[0].get('errors', ''))
                return results

            except (TTransportException, IOErrorException, RuntimeError,
                    NotValidConnectionException) as e:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug(
                        f"Connection to Nebula Graph is lost. It could be "
                        f"due to idle for too long, or network issue: { e }."
                        f"Trying to reconnect...")
                self.init_connection()
                raise e

            except Exception as e:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug(
                        'Failed executing query: %s, param: %s, except: %s',
                        query, str(param_dict), str(e))
                LOGGER.error('Failed executing query: %s', query)
                raise RuntimeError(str(e))

    # noinspection PyMethodMayBeStatic
    def _make_badges(self, badges: Iterable,
                     badges_meta: Iterable) -> List[Badge]:
        """
        Generates a list of Badges objects

        :param badges: A list of badges of a table, column, or type_metadata
        :return: a list of Badge objects
        """
        _badges = []
        for cursor, badge in enumerate(badges):
            _badges.append(
                Badge(badge_name=badges_meta[cursor]["id"],
                      category=badge["Badge.category"]))
        return _badges

    @timer_with_counter
    def get_resource_description(self, *, resource_type: ResourceType,
                                 uri: str) -> Description:
        """
        Get the resource description based on the uri. Any exception will propagate back to api server.

        :param resource_type:
        :param uri:
        :return:
        """

        description_query = Template(
            textwrap.dedent("""
            MATCH (n:`{{ resource_type }}`)-[:DESCRIPTION]->(d:Description)
            WHERE id(n) == "{{ vid }}"
            RETURN d.Description.description AS description;
            """))

        result = self._execute_query(
            query=description_query.render(resource_type=resource_type.name,
                                           vid=uri),
            param_dict={},
        )[0]
        data = result.get('data', [])
        description = None
        if len(data) > 0 and data[0].get('row', None) is not None:
            description_index = self._get_result_column_index(
                result, "description")
            description = data[0]['row'][description_index]
        return Description(description=description if data else None)

    @timer_with_counter
    def get_table_description(self, *, table_uri: str) -> Union[str, None]:
        """
        Get the table description based on table uri. Any exception will propagate back to api server.

        :param table_uri:
        :return:
        """

        return self.get_resource_description(resource_type=ResourceType.Table,
                                             uri=table_uri).description

    @timer_with_counter
    def get_type_metadata_description(
            self, *, type_metadata_key: str) -> Union[str, None]:
        """
        Get the type_metadata description based on its key. Any exception will propagate back to api server.

        :param type_metadata_key:
        :return:
        """

        return self.get_resource_description(
            resource_type=ResourceType.Type_Metadata,
            uri=type_metadata_key).description

    @timer_with_counter
    def put_resource_description(self, *, resource_type: ResourceType,
                                 uri: str, description: str) -> None:
        """
        Update resource description with one from user
        :param uri: Resource uri (Vertex ID in Nebula Graph)
        :param description: new value for resource description
        """
        desc_vid = uri + '/_description'

        description = re.escape(description)
        upsert_desc_query = Template(
            textwrap.dedent("""
        UPSERT EDGE ON DESCRIPTION_OF
        "{{ desc_vid }}" -> "{{ uri }}"
        SET START_LABEL = "Description",
            END_LABEL = "{{ resource_type }}"
        WHEN START_LABEL != "Description";

        UPSERT EDGE ON DESCRIPTION
        "{{ uri }}" -> "{{ desc_vid }}"
        SET END_LABEL = "Description",
            START_LABEL = "{{ resource_type }}"
        WHEN END_LABEL != "Description";

        UPSERT VERTEX ON `Description` "{{ desc_vid }}"
        SET `description` = '{{ description }}'
        WHEN description != '{{ description }}'
        YIELD description;
        """))

        self._execute_query(query=upsert_desc_query.render(
            description=description,
            uri=uri,
            desc_vid=desc_vid,
            resource_type=resource_type.name,
        ),
                            param_dict={})

    @timer_with_counter
    def put_table_description(self, *, table_uri: str,
                              description: str) -> None:
        """
        Update table description with one from user
        :param table_uri: Table uri (Vertex ID in Nebula Graph)
        :param description: new value for table description
        """

        self.put_resource_description(resource_type=ResourceType.Table,
                                      uri=table_uri,
                                      description=description)

    def put_type_metadata_description(self, *, type_metadata_key: str,
                                      description: str) -> None:
        """
        Update type_metadata description with one from user
        :param type_metadata_key:
        :param description:
        """
        self.put_resource_description(resource_type=ResourceType.Type_Metadata,
                                      uri=type_metadata_key,
                                      description=description)

    @timer_with_counter
    def get_column_description(self, *, table_uri: str,
                               column_name: str) -> Union[str, None]:
        """
        Get the column description based on table uri. Any exception will propagate back to api server.

        :param table_uri:
        :param column_name:
        :return:
        """

        column_vid = f"{ table_uri }/{ column_name }"
        column_description_query = Template(
            textwrap.dedent("""
            MATCH (tbl:Table)-[:COLUMN]->(c:Column)-[:DESCRIPTION]->(d:Description)
            WHERE id(tbl) == "{{ vid }}" AND id(c) == "{{ column_vid }}"
            RETURN d.Description.description AS description;
        """))

        result = self._execute_query(query=column_description_query.render(
            vid=table_uri, column_vid=column_vid),
                                     param_dict={})[0]
        data = result.get('data', None)
        description = None
        if data:
            description_index = self._get_result_column_index(
                result, "description")
            description = data[0]['row'][description_index]

        return description

    @timer_with_counter
    def put_column_description(self, *, table_uri: str, column_name: str,
                               description: str) -> None:
        """
        Update column description with input from user
        :param table_uri:
        :param column_name:
        :param description:
        :return:
        """

        column_uri = f"{ table_uri }/{ column_name }"

        self.put_resource_description(resource_type=ResourceType.Column,
                                      uri=column_uri,
                                      description=description)

    @timer_with_counter
    def add_owner(self, *, table_uri: str, owner: str) -> None:
        """
        Update table owner informations.
        1. Do a create if not exists query of the owner(`user`) node.
        2. Do a upsert of the owner/owned_by relation.
        :param table_uri:
        :param owner:
        :return:
        """

        self.add_resource_owner(uri=table_uri,
                                resource_type=ResourceType.Table,
                                owner=owner)

    @timer_with_counter
    def add_resource_owner(self, *, uri: str, resource_type: ResourceType,
                           owner: str) -> None:
        """
        Update table owner informations.
        1. Do a create if not exists query of the owner(`user`) node.
        2. Do a upsert of the owner/owned_by relation.

        :param table_uri:
        :param owner:
        :return:
        """
        user_email = owner
        create_owner_query = Template(
            textwrap.dedent("""
            UPSERT EDGE ON OWNER_OF
            "{{ user_email }}" -> "{{ uri }}"
            SET START_LABEL = "User",
                END_LABEL = "{{ resource_type }}"
            WHEN START_LABEL != "User";

            UPSERT EDGE ON OWNER
            "{{ uri }}" -> "{{ user_email }}"
            SET END_LABEL = "User",
                START_LABEL = "{{ resource_type }}"
            WHEN END_LABEL != "User";

            UPSERT VERTEX ON `User` "{{ user_email }}"
            SET email = "{{ user_email }}"
            WHEN email != "{{ user_email }}"
            YIELD email;
        """))

        self._execute_query(query=create_owner_query.render(
            user_email=user_email, uri=uri, resource_type=resource_type.name),
                            param_dict={})

    @timer_with_counter
    def delete_owner(self, *, table_uri: str, owner: str) -> None:
        """
        Delete the owner / owned_by relationship.
        :param table_uri:
        :param owner:
        :return:
        """
        self.delete_resource_owner(uri=table_uri,
                                   resource_type=ResourceType.Table,
                                   owner=owner)

    @timer_with_counter
    def delete_resource_owner(self, *, uri: str, resource_type: ResourceType,
                              owner: str) -> None:
        """
        Delete the owner / owned_by relationship.
        :param table_uri:
        :param owner:
        :return:
        """
        delete_query = Template(
            textwrap.dedent("""
            DELETE EDGE OWNER_OF "{{ owner }}" -> "{{ uri }}";
            DELETE EDGE OWNER "{{ uri }}" -> "{{ owner }}";
        """))

        self._execute_query(query=delete_query.render(owner=owner, uri=uri),
                            param_dict={})

    @timer_with_counter
    def add_badge(self,
                  *,
                  id: str,
                  badge_name: str,
                  category: str = '',
                  resource_type: ResourceType) -> None:

        LOGGER.info('New badge {} for id {} with category {} '
                    'and resource type {}'.format(badge_name, id, category,
                                                  resource_type.name))

        add_badge_query = Template(
            textwrap.dedent("""
            UPSERT EDGE ON BADGE_FOR
            "{{ badge_name }}" -> "{{ uri }}"
            SET START_LABEL = "Badge",
                END_LABEL = "{{ resource_type }}"
            WHEN START_LABEL != "Badge";

            UPSERT EDGE ON HAS_BADGE
            "{{ uri }}" -> "{{ badge_name }}"
            SET END_LABEL = "Badge",
                START_LABEL = "{{ resource_type }}"
            WHEN END_LABEL != "Badge";

            UPSERT VERTEX ON `Badge` "{{ badge_name }}"
            SET category = "{{ category }}"
            WHEN category != "{{ category }}"
            YIELD category;
        """))

        self._execute_query(query=add_badge_query.render(
            uri=id,
            badge_name=badge_name,
            category=category,
            resource_type=resource_type.name),
                            param_dict={})

    @timer_with_counter
    def delete_badge(self, id: str, badge_name: str, category: str,
                     resource_type: ResourceType) -> None:

        LOGGER.info('Delete badge {} for id {} with category {}'.format(
            badge_name, id, category))

        delete_query = Template(
            textwrap.dedent("""
            DELETE EDGE BADGE_FOR "{{ badge_name }}" -> "{{ uri }}";
            DELETE EDGE HAS_BADGE "{{ uri }}" -> "{{ badge_name }}";
        """))
        self._execute_query(query=delete_query.render(badge_name=badge_name,
                                                      uri=id),
                            param_dict={})

    @timer_with_counter
    def get_badges(self) -> List:
        LOGGER.info('Get all badges')
        query = textwrap.dedent("""
        MATCH (b:Badge) RETURN b AS badge
        """)
        records = self._execute_query(query=query, param_dict={})[0]
        index_badge = self._get_result_column_index(records, 'badge')
        results = []
        for record in records.get('data', []):
            results.append(
                Badge(badge_name=record['meta'][index_badge]['id'],
                      category=record['row'][index_badge]['Badge.category']))

        return results

    @timer_with_counter
    def add_tag(self,
                *,
                id: str,
                tag: str,
                tag_type: str = 'default',
                resource_type: ResourceType = ResourceType.Table) -> None:
        """
        Add new tag
        1. Create the node with type Tag if the node doesn't exist.
        2. Create the relation between tag and table if the relation doesn't exist.

        :param id:
        :param tag:
        :param tag_type:
        :param resource_type:
        :return: None
        """
        LOGGER.info(
            'New tag {} for id {} with type {} and resource type {}'.format(
                tag, id, tag_type, resource_type.name))

        add_tag_query = Template(
            textwrap.dedent("""
            UPSERT EDGE ON `TAG`
            "{{ tag }}" -> "{{ uri }}"
            SET START_LABEL = "Badge",
                END_LABEL = "{{ resource_type }}"
            WHEN START_LABEL != "Badge";

            UPSERT EDGE ON TAGGED_BY
            "{{ uri }}" -> "{{ tag }}"
            SET END_LABEL = "Badge",
                START_LABEL = "{{ resource_type }}"
            WHEN END_LABEL != "Badge";

            UPSERT VERTEX ON `Tag` "{{ tag }}"
            SET tag_type = "{{ tag_type }}"
            WHEN tag_type != "{{ tag_type }}"
            YIELD tag_type;
        """))

        self._execute_query(query=add_tag_query.render(
            uri=id,
            tag=tag,
            tag_type=tag_type,
            resource_type=resource_type.name),
                            param_dict={})

    @timer_with_counter
    def delete_tag(self,
                   *,
                   id: str,
                   tag: str,
                   tag_type: str = 'default',
                   resource_type: ResourceType = ResourceType.Table) -> None:
        """
        Deletes tag
        1. Delete the relation between resource and the tag
        2. todo(Tao): need to think about whether we should delete the tag if it is an orphan tag.
           todo(Wey): keep orphan tag not be deleted.

        :param id:
        :param tag:
        :param tag_type: {default-> normal tag, badge->non writable tag from UI}
        :param resource_type:
        :return:
        """

        LOGGER.info(
            'Delete tag {} for id {} with type {} and resource type: {}'.
            format(tag, id, tag_type, resource_type.name))
        delete_query = Template(
            textwrap.dedent("""
            DELETE EDGE `TAG` "{{ tag }}" -> "{{ uri }}";
            DELETE EDGE TAGGED_BY "{{ uri }}" -> "{{ tag }}";
        """))
        self._execute_query(query=delete_query.render(tag=tag, uri=id),
                            param_dict={})

    @timer_with_counter
    def get_tags(self) -> List:
        """
        Get all existing tags from Nebula

        :return:
        """
        LOGGER.info('Get all the tags')
        # todo: Currently all the tags are default type, we could open it up if we want to include badge
        query = textwrap.dedent("""
        MATCH (t:`Tag`{tag_type: 'default'})
        OPTIONAL MATCH (resource)-[:TAGGED_BY]->(t)
        WITH t AS tag_name, count(distinct id(resource)) AS tag_count
        WHERE tag_count > 0
        RETURN tag_name, tag_count
        """)

        records = self._execute_query(query=query, param_dict={})[0]
        i_tag_name, i_tag_count = self._get_result_column_indexes(
            records, ('tag_name', 'tag_count'))
        results = []
        for record in records.get('data', []):
            results.append(
                TagDetail(tag_name=record['meta'][i_tag_name]['id'],
                          tag_count=record['row'][i_tag_count]))
        return results

    @timer_with_counter
    def get_latest_updated_ts(self) -> Optional[int]:
        """
        API method to fetch last updated / index timestamp for Nebula, es

        :return:
        """
        query = textwrap.dedent("""
        MATCH (n:Updatedtimestamp)
        WHERE id(n) == 'amundsen_updated_timestamp'
        RETURN n
        """)
        record = self._execute_query(query=query, param_dict={})[0]
        index_n = self._get_result_column_index(record, 'n')
        if record.get('data', None):
            # There should be one and only one record
            ts = record['data'][0]['row'][index_n].get(
                "Updatedtimestamp.latest_timestamp", 0)
            if ts is None:
                return 0
            else:
                return ts
        else:
            return None

    @timer_with_counter
    def get_statistics(self) -> Dict[str, Any]:
        """
        API method to fetch statistics metrics for Nebula Graph
        :return: dictionary of statistics
        """
        query = textwrap.dedent("""
        MATCH (table_node:Table) with count(table_node) as number_of_tables
        MATCH p=(item_node:Table)-[:DESCRIPTION]->(description_node:Description)
        WHERE size(description_node.Description.description)>2 and exists(item_node.Table.is_view)
        with count(item_node) as number_of_documented_tables, number_of_tables
        MATCH p=(item_node:Column)-[:DESCRIPTION]->(description_node1:Description)
        WHERE size(description_node1.Description.description)>2 and exists(item_node.Column.sort_order)
        with count(item_node) as number_of_documented_cols, number_of_documented_tables, number_of_tables
        MATCH p=(table_node:Table)-[:OWNER]->(user_node:`User`) with count(distinct table_node) as number_of_tables_with_owners,
        count(distinct user_node) as number_of_owners, number_of_documented_cols,
        number_of_documented_tables, number_of_tables
        MATCH (item_node:Table)-[:DESCRIPTION]->(description_node:Description)
        WHERE  size(description_node.Description.description)>2 and exists(item_node.Table.is_view)
        MATCH (item_node:Table)-[:OWNER]->(user_node:`User`)
        with count(item_node) as number_of_documented_and_owned_tables,
        number_of_tables_with_owners, number_of_owners, number_of_documented_cols,
        number_of_documented_tables, number_of_tables
        RETURN number_of_tables, number_of_documented_tables, number_of_documented_cols,
        number_of_owners, number_of_tables_with_owners, number_of_documented_and_owned_tables
        """)
        LOGGER.info('Getting Nebula Graph Statistics')
        records = self._execute_query(query=query, param_dict={})[0]
        (i_number_of_tables, i_number_of_documented_tables,
         i_number_of_documented_cols, i_number_of_owners,
         i_number_of_tables_with_owners,
         i_number_of_documented_and_owned_tables
         ) = self._get_result_column_indexes(
             records, ('number_of_tables', 'number_of_documented_tables',
                       'number_of_documented_cols', 'number_of_owners',
                       'number_of_tables_with_owners',
                       'number_of_documented_and_owned_tables'))

        for record in records.get('data', []):
            r = record['row']
            nebula_statistics = {
                'number_of_tables':
                r[i_number_of_tables],
                'number_of_documented_tables':
                r[i_number_of_documented_tables],
                'number_of_documented_cols':
                r[i_number_of_documented_cols],
                'number_of_owners':
                r[i_number_of_owners],
                'number_of_tables_with_owners':
                r[i_number_of_tables_with_owners],
                'number_of_documented_and_owned_tables':
                r[i_number_of_documented_and_owned_tables]
            }
            return nebula_statistics
        return {}

    @_CACHE.cache('_get_global_popular_resources_uris',
                  expire=_GET_POPULAR_RESOURCES_CACHE_EXPIRY_SEC)
    def _get_global_popular_resources_uris(
            self,
            num_entries: int,
            resource_type: ResourceType = ResourceType.Table) -> List[str]:
        """
        Retrieve popular table uris. Will provide tables with top x popularity score.
        Popularity score = number of distinct readers * log(total number of reads)
        The result of this method will be cached based on the key (num_entries), and the cache will be expired based on
        _GET_POPULAR_TABLE_CACHE_EXPIRY_SEC

        For score computation, it uses logarithm on total number of reads so that score won't be affected by small
        number of users reading a lot of times.
        :return: Iterable of table uri
        """
        query = Template(
            textwrap.dedent("""
        MATCH (resource:`{{ resource_type }}`)-[r:READ_BY]->(u:`User`)
        WITH id(resource) AS vid, count(distinct u) AS readers, sum(r.read_count) AS total_reads
        WHERE readers >= {{ num_readers }}
        RETURN vid, readers, total_reads, (readers * log(total_reads)) AS score
        ORDER BY score DESC LIMIT {{ num_entries }};
        """))
        LOGGER.info('Querying popular tables URIs')
        num_readers = current_app.config[
            'POPULAR_RESOURCES_MINIMUM_READER_COUNT']

        records = self._execute_query(query=query.render(
            resource_type=resource_type.name,
            num_readers=num_readers,
            num_entries=num_entries),
                                      param_dict={})[0]

        i_vid = self._get_result_column_index(records, 'vid')
        return [record['row'][i_vid] for record in records.get('data', [])]

    @timer_with_counter
    @_CACHE.cache('_get_personal_popular_tables_uris',
                  _GET_POPULAR_RESOURCES_CACHE_EXPIRY_SEC)
    def _get_personal_popular_resources_uris(
            self,
            num_entries: int,
            user_id: str,
            resource_type: ResourceType = ResourceType.Table) -> List[str]:
        """
        Retrieve personalized popular resources uris. Will provide resources with top
        popularity score that have been read by a peer of the user_id provided.
        The popularity score is defined in the same way AS `_get_global_popular_resources_uris`

        The result of this method will be cached based on the key (num_entries, user_id),
        and the cache will be expired based on _GET_POPULAR_TABLE_CACHE_EXPIRY_SEC

        :return: Iterable of table uri
        """
        query = Template(
            textwrap.dedent("""
        MATCH (u:`User`)<-[:READ_BY]-(:`{{ resource_type }}`)-[:READ_BY]->
             (coUser:`User`)<-[coRead:READ_BY]-(resource:`{{ resource_type }}`)
        WHERE id(u) == "{{ user_id }}"
        WITH id(resource) AS vid, count(DISTINCT coUser) AS co_readers,
             sum(coRead.read_count) AS total_co_reads
        WHERE co_readers >= {{ num_readers }}
        RETURN vid, (co_readers * log(total_co_reads)) AS score
        ORDER BY score DESC LIMIT {{ num_entries }};
        """))
        LOGGER.info('Querying popular tables URIs')
        num_readers = current_app.config[
            'POPULAR_RESOURCES_MINIMUM_READER_COUNT']

        records = self._execute_query(query=query.render(
            resource_type=resource_type.name,
            user_id=user_id,
            num_readers=num_readers,
            num_entries=num_entries),
                                      param_dict={})[0]
        i_vid = self._get_result_column_index(records, 'vid')
        return [record['row'][i_vid] for record in records.get('data', [])]

    @timer_with_counter
    def get_popular_tables(
            self,
            *,
            num_entries: int,
            user_id: Optional[str] = None) -> List[PopularTable]:
        """

        Retrieve popular tables. AS popular table computation requires full scan of table and user relationship,
        it will utilize cached method _get_popular_tables_uris.

        :param num_entries:
        :return: Iterable of PopularTable
        """
        if user_id is None:
            # Get global popular table URIs
            table_uris = self._get_global_popular_resources_uris(num_entries)
        else:
            # Get personalized popular table URIs
            table_uris = self._get_personal_popular_resources_uris(
                num_entries, user_id)

        if not table_uris:
            return []

        # note(Wey) We render table_uris into list in string for now, will change to do from param_dict later

        query = Template(
            textwrap.dedent("""
        MATCH (db:Database)-[:CLUSTER]->(clstr:Cluster)-[:SCHEMA]->(schema:Schema)-[:TABLE]->(tbl:Table)
        WHERE id(tbl) IN {{ table_uris }}
        WITH db.Database.name AS database_name, clstr.Cluster.name AS cluster_name, schema.Schema.name AS schema_name, tbl
        OPTIONAL MATCH (tbl)-[:DESCRIPTION]->(dscrpt:Description)
        RETURN database_name, cluster_name, schema_name, tbl.Table.name AS table_name,
        dscrpt.Description.description AS table_description;
        """))

        records = self._execute_query(
            query=query.render(table_uris=str(table_uris)), param_dict={})[0]

        (i_database_name, i_cluster_name, i_schema_name, i_table_name,
         i_table_description) = self._get_result_column_indexes(
             records, ('database_name', 'cluster_name', 'schema_name',
                       'table_name', 'table_description'))

        popular_tables = []
        for record in records.get('data', []):
            r = record['row']
            popular_table = PopularTable(database=r[i_database_name],
                                         cluster=r[i_cluster_name],
                                         schema=r[i_schema_name],
                                         name=r[i_table_name],
                                         description=r[i_table_description])
            popular_tables.append(popular_table)
        return popular_tables

    def _get_popular_tables(self, *,
                            resource_uris: List[str]) -> List[TableSummary]:
        """

        """
        if not resource_uris:
            return []
        # note(Wey) We render resource_uris into list in string for now, will change to do from param_dict later

        query = Template(
            textwrap.dedent("""
        MATCH (db:Database)-[:CLUSTER]->(clstr:Cluster)-[:SCHEMA]->(schema:Schema)-[:TABLE]->(tbl:Table)
        WHERE id(tbl) IN {{ table_uris }}
        WITH db.Database.name AS database_name, clstr.Cluster.name AS cluster_name, schema.Schema.name AS schema_name, tbl
        OPTIONAL MATCH (tbl)-[:DESCRIPTION]->(dscrpt:Description)
        RETURN database_name, cluster_name, schema_name, tbl.Table.name AS table_name,
        dscrpt.DESCRIPTION.description AS table_description;
        """))
        records = self._execute_query(
            query=query.render(table_uris=str(resource_uris)),
            param_dict={})[0]

        (i_database_name, i_cluster_name, i_schema_name, i_table_name,
         i_table_description) = self._get_result_column_indexes(
             records, ('database_name', 'cluster_name', 'schema_name',
                       'table_name', 'table_description'))

        popular_tables = []
        for record in records.get('data', []):
            r = record['row']
            popular_table = TableSummary(database=r[i_database_name],
                                         cluster=r[i_cluster_name],
                                         schema=r[i_schema_name],
                                         name=r[i_table_name],
                                         description=r[i_table_description])
            popular_tables.append(popular_table)
        return popular_tables

    def _get_popular_dashboards(
            self, *, resource_uris: List[str]) -> List[DashboardSummary]:
        """

        """
        if not resource_uris:
            return []
        # note(Wey) We render resource_uris into list in string for now, will change to do from param_dict later
        query = Template(
            textwrap.dedent("""
        MATCH (d:Dashboard)-[:DASHBOARD_OF]->(dg:Dashboardgroup)-[:DASHBOARD_GROUP_OF]->(c:Cluster)
        WHERE id(d) IN {{ dashboards_uris }}
        OPTIONAL MATCH (d)-[:DESCRIPTION]->(dscrpt:Description)
        OPTIONAL MATCH (d)-[:EXECUTED]->(last_exec:Execution)
        WHERE split(id(last_exec), '/')[5] == '_last_successful_execution'
        RETURN c.Cluster.name AS cluster_name, dg.Dashboardgroup.name AS dg_name, dg.Dashboardgroup.dashboard_group_url AS dg_url,
        id(d) AS uri, d.Dashboard.name AS name, d.Dashboard.dashboard_url AS url,
        split(id(d), '_')[0] AS product,
        dscrpt.Description.description AS description, last_exec.Execution.`timestamp` AS last_successful_run_timestamp
        """))

        records = self._execute_query(
            query=query.render(dashboards_uris=str(resource_uris)),
            param_dict={})[0]

        (i_cluster_name, i_dg_name, i_dg_url, i_uri, i_name, i_url, i_product,
         i_description,
         i_last_successful_run_timestamp) = self._get_result_column_indexes(
             records,
             ('cluster_name', 'dg_name', 'dg_url', 'uri', 'name', 'url',
              'product', 'description', 'last_successful_run_timestamp'))

        popular_dashboards = []
        for record in records.get('data', []):
            r = record['row']
            popular_dashboard = DashboardSummary(
                uri=r[i_uri],
                cluster=r[i_cluster_name],
                group_name=r[i_dg_name],
                group_url=r[i_dg_url],
                product=r[i_product],
                name=r[i_name],
                url=r[i_url],
                description=r[i_description],
                last_successful_run_timestamp=r[
                    i_last_successful_run_timestamp])
            popular_dashboards.append(popular_dashboard)

        return popular_dashboards

    @timer_with_counter
    def get_popular_resources(
            self,
            *,
            num_entries: int,
            resource_types: List[str],
            user_id: Optional[str] = None) -> Dict[str, List]:
        popular_resources: Dict[str, List] = dict()
        for resource in resource_types:
            resource_type = to_resource_type(label=resource)
            popular_resources[resource_type.name] = list()
            if user_id is None:
                # Get global popular Table/Dashboard URIs
                resource_uris = self._get_global_popular_resources_uris(
                    num_entries, resource_type=resource_type)
            else:
                # Get personalized popular Table/Dashboard URIs
                resource_uris = self._get_personal_popular_resources_uris(
                    num_entries, user_id, resource_type=resource_type)

            if resource_type == ResourceType.Table:
                popular_resources[
                    resource_type.name] = self._get_popular_tables(
                        resource_uris=resource_uris)
            elif resource_type == ResourceType.Dashboard:
                popular_resources[
                    resource_type.name] = self._get_popular_dashboards(
                        resource_uris=resource_uris)

        return popular_resources

    @timer_with_counter
    def get_user(self, *, id: str) -> Union[UserEntity, None]:
        """
        Retrieve user detail based on `user`_id(email).

        :param id: the email for the given user
        :return:
        """

        query = Template(
            textwrap.dedent("""
        MATCH (u:`User`)
        WHERE id(u) == "{{ vid }}"
        OPTIONAL MATCH (u:`User`)-[:MANAGE_BY]->(manager:`User`)
        RETURN u AS user_record, manager AS manager_record
        """))

        record = self._execute_query(query=query.render(vid=id),
                                     param_dict={})[0]

        data = record.get('data', [])

        if not data:
            raise NotFoundException(
                'User {user_id} '
                'not found in the graph'.format(user_id=id))
        i_user_record, i_manager_record = self._get_result_column_indexes(
            record, ('user_record', 'manager_record'))

        user_record = data[0]['row'][i_user_record]
        manager_record = data[0]['row'][i_manager_record]
        self._format_record(user_record, ResourceType.User.name)

        if manager_record:
            self._format_record(manager_record, ResourceType.User.name)
            manager_name = manager_record.get('full_name', '')
        else:
            manager_name = ''

        return self._build_user_from_record(record=user_record,
                                            manager_name=manager_name)

    def create_update_user(self, *, user: User) -> Tuple[User, bool]:
        """
        Create a user if it does not exist, otherwise update the user. Required
        fields for creating / updating a user are validated upstream to this when
        the User object is created.

        :param user:
        :return:
        """
        user_data = UserSchema().dump(user)
        properties, values = self._create_props(user_data)

        user_query = Template(
            textwrap.dedent("""
            MATCH (u:`User`)
            WHERE id(u) == "{{ user_id }}"
            RETURN u
        """))

        user_result = self._execute_query(
            query=user_query.render(user_id=user.user_id), param_dict={})[0]

        user_existed = (len(user_result.get('data', [])) == 1)

        create_update_user_query = Template(
            textwrap.dedent("""
            INSERT VERTEX `User`
                ({{ properties }}, {{ CREATED_EPOCH_MS }})
                VALUES "{{ user_id }}":({{ values }})
        """))

        self._execute_query(query=create_update_user_query.render(
            properties=properties,
            values=values,
            user_id=user.user_id,
            timestamp=str(int(time.time()))),
                            param_dict={})[0]

        new_user_result = self._execute_query(
            query=user_query.render(user_id=user.user_id), param_dict={})[0]
        i_u = self._get_result_column_index(new_user_result, 'u')
        user_record = new_user_result['data'][0]['row'][i_u]
        self._format_record(user_record, ResourceType.User.name)

        new_user = self._build_user_from_record(user_record)

        return new_user, not user_existed

    @staticmethod
    def _create_props(record_dict: dict) -> Tuple[str, str]:
        """
        Creates a Nebula property name list string and value list string
        for Nebula Graph DML.
        """

        properties, values = [], []
        for k, v in record_dict.items():
            if v or v is False:
                properties.append(f"`{ k }`")
                if type(v) is str:
                    values.append(f'"{ v }"')
                else:
                    values.append(str(v))

        properties.append(PUBLISHED_PROPERTY_NAME)
        values.append(f'"api_create_update_user"')

        properties.append(LAST_UPDATED_EPOCH_MS)
        values.append(str(int(time.time())))

        return ', '.join(properties), ', '.join(values)

    def get_users(self) -> List[UserEntity]:
        # Note, this requires index on `User(is_active)`
        query = "MATCH (usr:`User`) WHERE usr.`User`.is_active == true RETURN collect(usr) AS users"
        result = self._execute_query(query=query, param_dict={})[0]
        i_users = self._get_result_column_index(result, 'users')

        users = []
        records = result['data'][0]['row'][i_users]
        for record in records:
            self._format_record(record, ResourceType.User.name)
            users.append(self._build_user_from_record(record))

        return users

    @staticmethod
    def _build_user_from_record(record: dict,
                                manager_name: Optional[str] = None
                                ) -> UserEntity:
        """
        Builds user record from query result. Other than the one defined in amundsen_common.models.user.User,
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
                          manager_fullname=record.get('manager_fullname',
                                                      manager_name),
                          other_key_values=other_key_values)

    @staticmethod
    def _get_user_resource_relationship_clause(
            relation_type: UserResourceRel,
            id: str = None,
            user_id: str = None,
            resource_type: ResourceType = ResourceType.Table
    ) -> Tuple[str, str]:
        """
        Returns the relationship clause and the where clause of a query between users and tables
        The User node is 'usr', the table node is 'tbl', and the relationship is 'rel'
        e.g. (usr:`User`)-[rel:READ]->(tbl:Table), (usr)-[rel:READ]->(tbl)
        """
        resource_matcher: str = ''
        user_matcher: str = ':`User`'
        where_clause: str = ''

        if id is not None:
            resource_matcher += ':{}'.format(resource_type.name)
            if id != '':
                where_clause += f'WHERE id(resource) == "{ id }" '

        if user_id is not None:
            if user_id != '':
                if where_clause.startswith('WHERE'):
                    where_clause += 'AND '
                else:
                    where_clause += 'WHERE '

                where_clause += f'id(usr) == "{ user_id }" '

        if relation_type == UserResourceRel.follow:
            relation = f'(resource{resource_matcher})-[r1:FOLLOWED_BY]->(usr{user_matcher})-[r2:FOLLOW]->' \
                       f'(resource{resource_matcher})'
        elif relation_type == UserResourceRel.own:
            relation = f'(resource{resource_matcher})-[r1:OWNER]->(usr{user_matcher})-[r2:OWNER_OF]->' \
                       f'(resource{resource_matcher})'
        elif relation_type == UserResourceRel.read:
            relation = f'(resource{resource_matcher})-[r1:READ_BY]->(usr{user_matcher})-[r2:READ]->' \
                       f'(resource{resource_matcher})'
        else:
            raise NotImplementedError(
                f'The relation type {relation_type} is not defined!')
        return relation, where_clause

    @staticmethod
    def _get_user_resource_edge_type(
            relation_type: UserResourceRel) -> Tuple[str, str]:

        if relation_type == UserResourceRel.follow:
            edge_type = "FOLLOW"
            reverse_edge_type = "FOLLOWED_BY"
        elif relation_type == UserResourceRel.own:
            edge_type = "OWNER_OF"
            reverse_edge_type = "OWNER"
        elif relation_type == UserResourceRel.read:
            edge_type = "READ"
            reverse_edge_type = "READ_BY"
        else:
            raise NotImplementedError(
                f'The relation type {relation_type} is not defined!')
        return edge_type, reverse_edge_type

    @timer_with_counter
    def get_dashboard_by_user_relation(self, *, user_email: str, relation_type: UserResourceRel) \
            -> Dict[str, List[DashboardSummary]]:
        """
        Retrieve all follow the Dashboard per user based on the relation.

        :param user_email: the email of the user
        :param relation_type: the relation between the user and the resource
        :return:
        """
        rel_clause, where_clause = self._get_user_resource_relationship_clause(
            relation_type=relation_type,
            id='',
            resource_type=ResourceType.Dashboard,
            user_id=user_email)

        # FYI, to extract last_successful_execution, it searches for its execution ID which is always
        # _last_successful_execution
        # https://github.com/amundsen-io/amundsendatabuilder/blob/master/databuilder/models/dashboard/dashboard_execution.py#L18
        # https://github.com/amundsen-io/amundsendatabuilder/blob/master/databuilder/models/dashboard/dashboard_execution.py#L24

        query = Template(
            textwrap.dedent("""
        MATCH {{ rel_clause }}<-[:DASHBOARD]-(dg:Dashboardgroup)<-[:DASHBOARD_GROUP]-(clstr:Cluster)
        {{ where_clause }}
        OPTIONAL MATCH (resource:Dashboard)-[:DESCRIPTION]->(dscrpt:Description)
        OPTIONAL MATCH (resource:Dashboard)-[:EXECUTED]->(last_exec:Execution)
        WHERE split(id(last_exec), '/')[5] == '_last_successful_execution'
        RETURN clstr.Cluster.name AS cluster_name, dg.Dashboardgroup.name AS dg_name, dg.Dashboardgroup.dashboard_group_url AS dg_url,
        id(resource) AS uri, resource.Dashboard.name AS name, resource.Dashboard.dashboard_url AS url,
        split(id(resource), '_')[0] AS product,
        dscrpt.Description.description AS description, last_exec.Execution.`timestamp` AS last_successful_run_timestamp"""
                            ))

        records = self._execute_query(query=query.render(
            rel_clause=rel_clause, where_clause=where_clause),
                                      param_dict={})[0]

        data_records = records.get('data', [])
        if not data_records:
            raise NotFoundException(
                'User {user_id} does not {relation} on {resource_type} resources'
                .format(user_id=user_email,
                        relation=relation_type,
                        resource_type=ResourceType.Dashboard.name))

        results = []
        (i_cluster_name, i_dg_name, i_dg_url, i_uri, i_name, i_url, i_product,
         i_description,
         i_last_successful_run_timestamp) = self._get_result_column_indexes(
             records,
             ('cluster_name', 'dg_name', 'dg_url', 'uri', 'name', 'url',
              'product', 'description', 'last_successful_run_timestamp'))
        for record in data_records:
            data = record['row']
            results.append(
                DashboardSummary(
                    uri=data[i_uri],
                    cluster=data[i_cluster_name],
                    group_name=data[i_dg_name],
                    group_url=data[i_dg_url],
                    product=data[i_product],
                    name=data[i_name],
                    url=data[i_url],
                    description=data[i_description],
                    last_successful_run_timestamp=data[
                        i_last_successful_run_timestamp],
                ))

        return {ResourceType.Dashboard.name.lower(): results}

    @timer_with_counter
    def get_table_by_user_relation(self, *, user_email: str, relation_type: UserResourceRel) \
            -> Dict[str, List[PopularTable]]:
        """
        Retrive all follow the Table per user based on the relation.

        :param user_email: the email of the user
        :param relation_type: the relation between the user and the resource
        :return:
        """
        rel_clause, where_clause = self._get_user_resource_relationship_clause(
            relation_type=relation_type,
            id='',
            resource_type=ResourceType.Table,
            user_id=user_email)

        query = Template(
            textwrap.dedent("""
            MATCH {{ rel_clause }}<-[:TABLE]-(schema:Schema)<-[:SCHEMA]-(clstr:Cluster)<-[:CLUSTER]-(db:Database)
            {{ where_clause }}
            WITH db, clstr, schema, resource
            OPTIONAL MATCH (resource:Table)-[:DESCRIPTION]->(tbl_dscrpt:Description)
            RETURN db, clstr, schema, resource, tbl_dscrpt"""))

        records = self._execute_query(query=query.render(
            rel_clause=rel_clause, where_clause=where_clause),
                                      param_dict={})[0]

        data_records = records.get('data', [])
        if not data_records:
            raise NotFoundException(
                'User {user_id} does not {relation} any resources'.format(
                    user_id=user_email, relation=relation_type))
        results = []

        (i_db, i_clstr, i_schema, i_resource,
         i_tbl_dscrpt) = self._get_result_column_indexes(
             records, ('db', 'clstr', 'schema', 'resource', 'tbl_dscrpt'))
        for record in data_records:
            data = record['row']
            description = data[i_tbl_dscrpt].get(
                'Description.description', '') if data[i_tbl_dscrpt] else None
            results.append(
                PopularTable(database=data[i_db]['Database.name'],
                             cluster=data[i_clstr]['Cluster.name'],
                             schema=data[i_schema]['Schema.name'],
                             name=data[i_resource]['Table.name'],
                             description=description))

        return {ResourceType.Table.name.lower(): results}

    @timer_with_counter
    def get_frequently_used_tables(self, *, user_email: str) -> Dict[str, Any]:
        """
        Retrieves all Table the resources per user on READ relation.

        :param user_email: the email of the user
        :return:
        """

        query = Template(
            textwrap.dedent("""
        MATCH (u:`User`)-[r:READ]->(tbl:Table)
        WHERE id(u) == "{{ vid }}" AND EXISTS(r.published_tag) AND r.published_tag IS NOT NULL
        WITH u, r, tbl, r.published_tag AS published_tag, r.read_count AS read_count
            ORDER BY published_tag DESC, read_count DESC LIMIT 50
        MATCH (tbl:Table)<-[:TABLE]-(schema:Schema)<-[:SCHEMA]-(clstr:Cluster)<-[:CLUSTER]-(db:Database)
        OPTIONAL MATCH (tbl)-[:DESCRIPTION]->(tbl_dscrpt:Description)
        RETURN db, clstr, schema, tbl, tbl_dscrpt
        """))

        table_records = self._execute_query(query=query.render(vid=user_email),
                                            param_dict={})[0]

        data_records = table_records.get('data', [])

        if not data_records:
            raise NotFoundException(
                'User {user_id} does not READ any resources'.format(
                    user_id=user_email))
        results = []

        (i_db, i_clstr, i_schema, i_tbl,
         i_tbl_dscrpt) = self._get_result_column_indexes(
             table_records, ('db', 'clstr', 'schema', 'tbl', 'tbl_dscrpt'))
        for record in data_records:
            data = record['row']
            description = data[i_tbl_dscrpt].get(
                'Description.description', '') if data[i_tbl_dscrpt] else None
            results.append(
                PopularTable(database=data[i_db]['Database.name'],
                             cluster=data[i_clstr]['Cluster.name'],
                             schema=data[i_schema]['Schema.name'],
                             name=data[i_tbl]['Table.name'],
                             description=description))

        return {'table': results}

    @timer_with_counter
    def add_resource_relation_by_user(self, *, id: str, user_id: str,
                                      relation_type: UserResourceRel,
                                      resource_type: ResourceType) -> None:
        """
        Update table user informations.
        1. Do a upsert of the user node.
        2. Do a upsert of the relation/reverse-relation edge.

        :param table_uri:
        :param user_id:
        :param relation_type:
        :return:
        """
        edge_type, reverse_edge_type = self._get_user_resource_edge_type(
            relation_type=relation_type)

        query = Template(
            textwrap.dedent("""
        UPSERT EDGE ON `{{ edge_type }}`
        "{{ user_email }}" -> "{{ resource_id }}"
        SET START_LABEL = "User",
            END_LABEL = "{{ resource_type }}"
        WHEN START_LABEL != "User" OR END_LABEL != "{{ resource_type }}"
        YIELD START_LABEL, END_LABEL;

        UPSERT EDGE ON `{{ reverse_edge_type }}`
        "{{ resource_id }}" -> "{{ user_email }}"
        SET END_LABEL = "User",
            START_LABEL = "{{ resource_type }}"
        WHEN END_LABEL != "User" OR START_LABEL != "{{ resource_type }}"
        YIELD START_LABEL, START_LABEL;

        UPSERT VERTEX ON `User` "{{ user_email }}"
        SET email = "{{ user_email }}"
        WHEN email != "{{ user_email }}"
        YIELD email;

        UPSERT VERTEX ON `{{ resource_type }}` "{{ resource_id }}"
        SET name = "{{ user_email }}"
        WHEN name != "{{ user_email }}"
        YIELD name;
        """))

        result = self._execute_query(query=query.render(
            user_email=user_id,
            resource_id=id,
            resource_type=resource_type.name,
            edge_type=edge_type,
            reverse_edge_type=reverse_edge_type),
                                     param_dict={})[0]

        if not result.get('data', False):
            raise RuntimeError('Failed to create relation between '
                               'user {user} and resource {id}'.format(
                                   user=user_id, id=id))

    @timer_with_counter
    def delete_resource_relation_by_user(self, *, id: str, user_id: str,
                                         relation_type: UserResourceRel,
                                         resource_type: ResourceType) -> None:
        """
        Delete the relationship between user and resources.

        :param id:
        :param user_id:
        :param relation_type:
        :return:
        """
        edge_type, reverse_edge_type = self._get_user_resource_edge_type(
            relation_type=relation_type)

        delete_query = Template(
            textwrap.dedent("""
            DELETE EDGE `{{ edge_type }}` "{{ user_id }}" -> "{{ id }}";
            DELETE EDGE `{{ reverse_edge_type }}` "{{ id }}" -> "{{ user_id }}";
            """))

        self._execute_query(query=delete_query.render(
            edge_type=edge_type,
            reverse_edge_type=reverse_edge_type,
            user_id=user_id,
            id=id),
                            param_dict={})[0]

    @timer_with_counter
    def get_dashboard(
        self,
        id: str,
    ) -> DashboardDetailEntity:
        get_dashboard_detail_query = Template(
            textwrap.dedent("""
        MATCH (d:Dashboard)-[:DASHBOARD_OF]->(dg:Dashboardgroup)-[:DASHBOARD_GROUP_OF]->(c:Cluster)
        WHERE id(d) == "{{ id }}"
        OPTIONAL MATCH (d:Dashboard)-[:DESCRIPTION]->(description:Description)
        OPTIONAL MATCH (d:Dashboard)-[:EXECUTED]->(last_exec:Execution) WHERE split(id(last_exec), '/')[5] == '_last_execution'
        OPTIONAL MATCH (d:Dashboard)-[:EXECUTED]->(last_success_exec:Execution)
        WHERE split(id(last_success_exec), '/')[5] == '_last_successful_execution'
        OPTIONAL MATCH (d:Dashboard)-[:LAST_UPDATED_AT]->(t:`Timestamp`)
        OPTIONAL MATCH (d:Dashboard)-[:OWNER]->(owner:`User`)
        WITH c, dg, d, description, last_exec, last_success_exec, t, collect(owner) AS owners
        OPTIONAL MATCH (d:Dashboard)-[:TAGGED_BY]->(`tag`:`Tag`{tag_type: "default"})
        OPTIONAL MATCH (d:Dashboard)-[:HAS_BADGE]->(badge:Badge)
        WITH c, dg, d, description, last_exec, last_success_exec, t, owners, collect(`tag`) AS `tags`,
        collect(badge) AS badges
        OPTIONAL MATCH (d:Dashboard)-[read:READ_BY]->(:`User`)
        WITH c, dg, d, description, last_exec, last_success_exec, t, owners, `tags`, badges,
        sum(read.read_count) AS recent_view_count
        OPTIONAL MATCH (d:Dashboard)-[:HAS_QUERY]->(`query`:`Query`)
        WITH c, dg, d, description, last_exec, last_success_exec, t, owners, `tags`, badges,
        recent_view_count, collect({name: `query`.`Query`.name, url: `query`.`Query`.url, query_text: `query`.`Query`.query_text}) AS queries
        OPTIONAL MATCH (d:Dashboard)-[:HAS_QUERY]->(`query`:`Query`)-[:HAS_CHART]->(chart:Chart)
        WITH c, dg, d, description, last_exec, last_success_exec, t, owners, `tags`, badges,
        recent_view_count, queries, collect(chart) AS charts
        OPTIONAL MATCH (d:Dashboard)-[:DASHBOARD_WITH_TABLE]->(table:Table)<-[:TABLE]-(schema:Schema)
        <-[:SCHEMA]-(cluster:Cluster)<-[:CLUSTER]-(db:Database)
        OPTIONAL MATCH (table:Table)-[:DESCRIPTION]->(table_description:Description)
        WITH c, dg, d, description, last_exec, last_success_exec, t, owners, `tags`, badges,
        recent_view_count, queries, charts,
        collect({name: table.Table.name, schema: schema.Schema.name, cluster: cluster.Cluster.name, database: db.Database.name,
        description: table_description.Description.description}) AS tables
        RETURN
        c.Cluster.name AS cluster_name,
        id(d) AS uri,
        d.Dashboard.dashboard_url AS url,
        d.Dashboard.name AS name,
        split(id(d), '_')[0] AS product,
        d.Dashboard.created_timestamp AS created_timestamp,
        description.Dashboard.description AS description,
        dg.Dashboardgroup.name AS group_name,
        dg.Dashboardgroup.dashboard_group_url AS group_url,
        last_success_exec.Execution.`timestamp` AS last_successful_run_timestamp,
        last_exec.Execution.`timestamp` AS last_run_timestamp,
        last_exec.Execution.state AS last_run_state,
        t.`Timestamp`.`timestamp` AS updated_timestamp,
        owners,
        `tags`,
        badges,
        recent_view_count,
        queries,
        charts,
        tables;
        """))

        dashboard_record = self._execute_query(
            query=get_dashboard_detail_query.render(id=id), param_dict={})[0]
        # Hardcode as default for now.
        # param_dict={"tag_normal_type": NebulaValue(sVal="default")})[0]

        data_records = dashboard_record.get('data', [])

        if not data_records:
            raise NotFoundException(
                'No dashboard exist with URI: {}'.format(id))

        (i_uri, i_cluster_name, i_url, i_name, i_product, i_created_timestamp,
         i_description, i_group_name, i_group_url,
         i_last_successful_run_timestamp, i_last_run_timestamp,
         i_last_run_state, i_updated_timestamp, i_owners, i_tags, i_badges,
         i_recent_view_count, i_queries,
         i_charts, i_tables) = self._get_result_column_indexes(
             dashboard_record,
             ('uri', 'cluster_name', 'url', 'name', 'product',
              'created_timestamp', 'description', 'group_name', 'group_url',
              'last_successful_run_timestamp', 'last_run_timestamp',
              'last_run_state', 'updated_timestamp', 'owners', 'tags',
              'badges', 'recent_view_count', 'queries', 'charts', 'tables'))

        record = data_records[0]['row']
        meta = data_records[0]['meta']

        owners = []
        for owner in record[i_owners]:
            self._format_record(owner, ResourceType.User.name)
            owner_data = self._get_user_details(user_id=owner['email'],
                                                user_data=owner)
            owners.append(self._build_user_from_record(record=owner_data))

        tags = []
        for i, tag_record in enumerate(record[i_tags]):
            if meta[i_tags][i] and meta[i_tags][i].get("id", None):
                tag_result = Tag(tag_name=meta[i_tags][i]['id'],
                                 tag_type=tag_record['Tag.tag_type'])
                tags.append(tag_result)

        badges = self._make_badges(record[i_badges], meta[i_badges])

        chart_names = [
            chart['Chart.name'] for chart in record[i_charts]
            if 'Chart.name' in chart and chart['Chart.name']
        ]
        # TODO Deprecate query_names in favor of queries after several releases from v2.5.0
        query_names = [
            query['name'] for query in record[i_queries]
            if 'name' in query and query['name']
        ]
        queries = [
            DashboardQueryEntity(**query) for query in record[i_queries]
            if query.get('name') or query.get('url') or query.get('text')
        ]
        tables = [
            PopularTable(**table) for table in record[i_tables]
            if 'name' in table and table['name']
        ]

        return DashboardDetailEntity(
            uri=record[i_uri],
            cluster=record[i_cluster_name],
            url=record[i_url],
            name=record[i_name],
            product=record[i_product],
            created_timestamp=int(record[i_created_timestamp])
            if record[i_created_timestamp] else None,
            description=record[i_description],
            group_name=record[i_group_name],
            group_url=record[i_group_url],
            last_successful_run_timestamp=record[
                i_last_successful_run_timestamp],
            last_run_timestamp=int(record[i_last_run_timestamp])
            if record[i_last_run_timestamp] else None,
            last_run_state=record[i_last_run_state],
            updated_timestamp=int(record[i_updated_timestamp])
            if record[i_updated_timestamp] else None,
            owners=owners if owners else None,
            tags=tags if tags else None,
            badges=badges if badges else None,
            recent_view_count=int(record[i_recent_view_count])
            if record[i_recent_view_count] else None,
            chart_names=chart_names if chart_names else None,
            query_names=query_names if query_names else None,
            queries=queries if queries else None,
            tables=tables if tables else None)

    @timer_with_counter
    def get_dashboard_description(self, *, id: str) -> Description:
        """
        Get the dashboard description based on dashboard uri. Any exception will propagate back to api server.

        :param id:
        :return:
        """

        return self.get_resource_description(
            resource_type=ResourceType.Dashboard, uri=id)

    @timer_with_counter
    def put_dashboard_description(self, *, id: str, description: str) -> None:
        """
        Update Dashboard description
        :param id: Dashboard URI
        :param description: new value for Dashboard description
        """

        self.put_resource_description(resource_type=ResourceType.Dashboard,
                                      uri=id,
                                      description=description)

    @timer_with_counter
    def get_resources_using_table(
            self, *, id: str,
            resource_type: ResourceType) -> Dict[str, List[DashboardSummary]]:
        """

        :param id:
        :param resource_type:
        :return:
        """
        if resource_type != ResourceType.Dashboard:
            raise NotImplementedError(
                '{} is not supported'.format(resource_type))

        get_dashboards_using_table_query = Template(
            textwrap.dedent("""
        MATCH (d:Dashboard)-[:DASHBOARD_WITH_TABLE]->(table:Table),
        (d)-[:DASHBOARD_OF]->(dg:Dashboardgroup)-[:DASHBOARD_GROUP_OF]->(c:Cluster)
        WHERE id(table) == "{{ id }}"
        OPTIONAL MATCH (d)-[:DESCRIPTION]->(description:Description)
        OPTIONAL MATCH (d)-[:EXECUTED]->(last_success_exec:Execution)
        WHERE split(id(last_success_exec), '/')[5] == '_last_successful_execution'
        OPTIONAL MATCH (d)-[read:READ_BY]->(:`User`)
        WITH c, dg, d, description, last_success_exec, sum(read.read_count) AS recent_view_count
        RETURN
        id(d) AS uri,
        c.Cluster.name AS cluster,
        dg.Dashboardgroup.name AS group_name,
        dg.Dashboardgroup.dashboard_group_url AS group_url,
        d.Dashboard.name AS name,
        d.Dashboard.dashboard_url AS url,
        description.Description.description AS description,
        split(id(d), '_')[0] AS product,
        toInteger(last_success_exec.Execution.`timestamp`) AS last_successful_run_timestamp, recent_view_count
        ORDER BY recent_view_count DESC;
        """))

        records = self._execute_query(
            query=get_dashboards_using_table_query.render(id=id),
            param_dict={})[0]

        data_records = records.get('data', [])

        results = []
        (
            i_uri,
            i_cluster,
            i_group_name,
            i_group_url,
            i_name,
            i_url,
            i_description,
            i_product,
            i_last_successful_run_timestamp,
        ) = self._get_result_column_indexes(
            records,
            ('uri', 'cluster', 'group_name', 'group_url', 'name', 'url',
             'description', 'product', 'last_successful_run_timestamp'))

        for record in data_records:
            data = record['row']
            results.append(
                DashboardSummary(uri=data[i_uri],
                                 cluster=data[i_cluster],
                                 group_name=data[i_group_name],
                                 group_url=data[i_group_url],
                                 name=data[i_name],
                                 url=data[i_url],
                                 description=data[i_description],
                                 product=data[i_product],
                                 last_successful_run_timestamp=data[
                                     i_last_successful_run_timestamp]))

        return {'dashboards': results}

    @timer_with_counter
    def get_lineage(self,
                    *,
                    id: str,
                    resource_type: ResourceType,
                    direction: str,
                    depth: int = 1) -> Lineage:
        """
        Retrieves the lineage information for the specified resource type.

        :param id: key of a table or a column
        :param resource_type: Type of the entity for which lineage is being retrieved
        :param direction: Whether to get the upstream/downstream or both directions
        :param depth: depth or level of lineage information
        :return: The Lineage object with upstream & downstream lineage items
        """

        get_both_lineage_query = Template(
            textwrap.dedent("""
        MATCH (source:`{{ resource }}`)
        WHERE id(source) == "{{ id }}"
        OPTIONAL MATCH dpath=(source)-[downstream_len:HAS_DOWNSTREAM*..{{ depth }}]->(downstream_entity:`{{ resource }}`)
        OPTIONAL MATCH upath=(source)-[upstream_len:HAS_UPSTREAM*..{{ depth }}]->(upstream_entity:`{{ resource }}`)
        WITH downstream_entity, upstream_entity, downstream_len, upstream_len, upath, dpath
        OPTIONAL MATCH (upstream_entity)-[:HAS_BADGE]->(upstream_badge:Badge)
        OPTIONAL MATCH (downstream_entity)-[:HAS_BADGE]->(downstream_badge:Badge)
        WITH CASE WHEN downstream_badge IS NULL THEN collect(NULL)
        ELSE collect(distinct {key:id(downstream_badge),category:downstream_badge.Badge.category})
        END AS downstream_badges, CASE WHEN upstream_badge IS NULL THEN collect(NULL)
        ELSE collect(distinct {key:id(upstream_badge),category:upstream_badge.Badge.category})
        END AS upstream_badges, upstream_entity, downstream_entity, upstream_len, downstream_len, upath, dpath
        OPTIONAL MATCH (downstream_entity:`{{ resource }}`)-[downstream_read:READ_BY]->(:`User`)
        WITH upstream_entity, downstream_entity, upstream_len, downstream_len, upath, dpath,
        downstream_badges, upstream_badges, sum(downstream_read.read_count) as downstream_read_count
        OPTIONAL MATCH (upstream_entity:`{{ resource }}`)-[upstream_read:READ_BY]->(:`User`)
        WITH upstream_entity, downstream_entity, upstream_len, downstream_len,
        downstream_badges, upstream_badges, downstream_read_count,
        sum(upstream_read.read_count) as upstream_read_count, upath, dpath
        WITH CASE WHEN ALL(up_len in upstream_len WHERE up_len IS NULL) THEN collect(NULL)
        ELSE COLLECT(distinct {level:SIZE(upstream_len), source:split(id(upstream_entity),'://')[0],
        key:id(upstream_entity), badges:upstream_badges, usage:upstream_read_count, parent:id(nodes(upath)[-2])})
        END AS upstream_entities, CASE WHEN ALL(down_len in downstream_len WHERE down_len IS NULL) THEN collect(NULL)
        ELSE COLLECT(distinct {level:SIZE(downstream_len), source:split(id(downstream_entity),'://')[0],
        key:id(downstream_entity), badges:downstream_badges, usage:downstream_read_count, parent:id(nodes(dpath)[-2])})
        END AS downstream_entities RETURN downstream_entities, upstream_entities
        """))

        get_upstream_lineage_query = Template(
            textwrap.dedent("""
        MATCH (source:`{{ resource }}`)
        WHERE id(source) == "{{ id }}"
        OPTIONAL MATCH `path`=(source)-[upstream_len:HAS_UPSTREAM*..{{ depth }}]->(upstream_entity:`{{ resource }}`)
        WITH upstream_entity, upstream_len, `path`
        OPTIONAL MATCH (upstream_entity)-[:HAS_BADGE]->(upstream_badge:Badge)
        WITH CASE WHEN upstream_badge IS NULL THEN collect(NULL)
        ELSE collect(distinct {key:id(upstream_badge),category:upstream_badge.Badge.category})
        END AS upstream_badges, upstream_entity, upstream_len, `path`
        OPTIONAL MATCH (upstream_entity:`{{ resource }}`)-[upstream_read:READ_BY]->(:`User`)
        WITH upstream_entity, upstream_len, upstream_badges,
        sum(upstream_read.read_count) AS upstream_read_count, `path`
        WITH CASE WHEN ALL(up_len in upstream_len WHERE up_len IS NULL) THEN collect(NULL)
        ELSE COLLECT(distinct{level:SIZE(upstream_len), source:split(id(upstream_entity),'://')[0],
        key:id(upstream_entity), badges:upstream_badges, usage:upstream_read_count, parent:id(nodes(`path`)[-2])})
        END AS upstream_entities RETURN upstream_entities
        """))

        get_downstream_lineage_query = Template(
            textwrap.dedent("""
        MATCH (source:`{{ resource }}`)
        WHERE id(source) == "{{ id }}"
        OPTIONAL MATCH `path`=(source)-[downstream_len:HAS_DOWNSTREAM*..{{ depth }}]->(downstream_entity:`{{ resource }}`)
        WITH downstream_entity, downstream_len, `path`
        OPTIONAL MATCH (downstream_entity)-[:HAS_BADGE]->(downstream_badge:Badge)
        WITH CASE WHEN downstream_badge IS NULL THEN collect(NULL)
        ELSE collect(distinct {key:id(downstream_badge),category:downstream_badge.Badge.category})
        END AS downstream_badges, downstream_entity, downstream_len, `path`
        OPTIONAL MATCH (downstream_entity:`{{ resource }}`)-[downstream_read:READ_BY]->(:`User`)
        WITH downstream_entity, downstream_len, downstream_badges,
        sum(downstream_read.read_count) AS downstream_read_count, `path`
        WITH CASE WHEN ALL(down_len in downstream_len WHERE down_len IS NULL) THEN collect(NULL)
        ELSE COLLECT(distinct{level:SIZE(downstream_len), source:split(id(downstream_entity),'://')[0],
        key:id(downstream_entity), badges:downstream_badges, usage:downstream_read_count, parent:id(nodes(`path`)[-2])})
        END AS downstream_entities RETURN downstream_entities
        """))

        if direction == 'upstream':
            lineage_query = get_upstream_lineage_query

        elif direction == 'downstream':
            lineage_query = get_downstream_lineage_query

        else:
            lineage_query = get_both_lineage_query

        records = self._execute_query(query=lineage_query.render(
            depth=depth, resource=resource_type.name, id=id),
                                      param_dict={})[0]

        downstream_tables = []
        upstream_tables = []

        data_record = records.get('data', [])
        if data_record and "downstream_entities" in records['columns']:
            i_downstream_entities = self._get_result_column_index(
                records, "downstream_entities")
            for downstream in data_record[0]['row'][i_downstream_entities]:
                if downstream.get('key') is not None:
                    downstream_tables.append(
                        LineageItem(
                            **{
                                "key": downstream["key"],
                                "source": downstream["source"],
                                "level": downstream["level"],
                                "badges": downstream.get("badges", None),
                                "usage": downstream.get("usage", 0),
                                "parent": downstream.get("parent", '')
                            }))

        if data_record and "upstream_entities" in records['columns']:
            i_upstream_entities = self._get_result_column_index(
                records, "upstream_entities")
            for upstream in data_record[0]['row'][i_upstream_entities]:
                if upstream.get('key') is not None:
                    upstream_tables.append(
                        LineageItem(
                            **{
                                "key": upstream["key"],
                                "source": upstream["source"],
                                "level": upstream["level"],
                                "badges": upstream.get("badges", None),
                                "usage": upstream.get("usage", 0),
                                "parent": upstream.get("parent", '')
                            }))

        # ToDo: Add a root_entity AS an item, which will make it easier for lineage graph
        return Lineage(
            **{
                "key": id,
                "upstream_entities": upstream_tables,
                "downstream_entities": downstream_tables,
                "direction": direction,
                "depth": depth
            })

    def _create_watermarks(self, wmk_records: List) -> List[Watermark]:
        watermarks = []
        for record in wmk_records:
            if record['key'] is not None:
                watermark_type = record['key'].split('/')[-2]
                watermarks.append(
                    Watermark(watermark_type=watermark_type,
                              partition_key=record['partition_key'],
                              partition_value=record['partition_value'],
                              create_time=record['create_time']))
        return watermarks

    def _create_feature_watermarks(self, wmk_records: List,
                                   wmk_meta: List) -> List[Watermark]:
        watermarks = []
        for i, record in enumerate(wmk_records):
            if wmk_meta[i] and wmk_meta[i].get('id', None) is not None:
                watermark_type = wmk_meta[i].get('id').split('/')[-1]
                # Note(wey), the data from databuilder is in different model
                # comparing to it was defined in amundsen common
                # i.e. time vs timestamp
                watermarks.append(
                    FeatureWatermark(
                        key=wmk_meta[i].get('id'),
                        watermark_type=watermark_type,
                        time=record.get('Feature_Watermark.time', None)
                        or record.get('Feature_Watermark.timestamp', None)))
        return watermarks

    def _create_programmatic_descriptions(
            self, prog_desc_records: List) -> List[ProgrammaticDescription]:
        programmatic_descriptions = []
        for pg in prog_desc_records:
            source = pg.get('Programmatic_Description.description_source',
                            None)
            if source is None:
                LOGGER.error(
                    "A programmatic description with no source was found... skipping."
                )
            else:
                programmatic_descriptions.append(
                    ProgrammaticDescription(
                        source=source,
                        text=pg.get('Programmatic_Description.description',
                                    None)))

        return programmatic_descriptions

    def _create_owners(self, owner_records: List) -> List[User]:
        owners = []
        for owner in owner_records:
            owners.append(
                User(email=owner.get('User.email', None)
                     or owner.get('User.user_id', None), ))
        return owners

    def _create_app(self, app_record: dict, kind: str, id: str) -> Application:
        return Application(
            name=app_record['Application.name'],
            id=id,
            application_url=app_record['Application.application_url'],
            description=app_record.get('Application.description'),
            kind=kind,
        )

    def _create_apps(
        self, producing_app_records: Tuple[List],
        consuming_app_records: Tuple[List]
    ) -> Tuple[Application, List[Application]]:

        table_apps = []
        producing_records, producing_meta = producing_app_records
        for i, record in enumerate(producing_records):
            table_apps.append(
                self._create_app(record,
                                 kind='Producing',
                                 id=producing_meta[i].get('id')))

        # for bw compatibility, we populate table_writer with one of the producing apps
        table_writer = table_apps[0] if table_apps else None

        _producing_app_ids = {app.id for app in table_apps}
        consuming_records, consuming_meta = consuming_app_records

        for i, record in enumerate(consuming_records):
            # if an app has both a consuming and producing relationship with a table
            # (e.g. an app that reads writes back to its input table), we call it a Producing app and
            # do not add it again
            record_id = consuming_meta[i].get('id')
            if record_id not in _producing_app_ids:
                table_apps.append(
                    self._create_app(record, kind='Consuming', id=record_id))

        return table_writer, table_apps

    @timer_with_counter
    def _exec_feature_query(self, *, feature_key: str) -> Dict:
        """
        Executes query to get feature and related nodes
        """

        feature_query = Template(
            textwrap.dedent("""
        MATCH (feat:Feature)
        WHERE id(feat) == "{{ feature_key }}"
        OPTIONAL MATCH (db:Database)-[:AVAILABLE_FEATURE]->(feat)
        OPTIONAL MATCH (fg:Feature_Group)-[:`GROUPS`]->(feat)
        OPTIONAL MATCH (feat:Feature)-[:OWNER]->(owner:`User`)
        OPTIONAL MATCH (feat:Feature)-[:TAGGED_BY]->(`tag`:`Tag`)
        OPTIONAL MATCH (feat:Feature)-[:HAS_BADGE]->(badge:Badge)
        OPTIONAL MATCH (feat:Feature)-[:DESCRIPTION]->(description:Description)
        OPTIONAL MATCH (feat:Feature)-[:DESCRIPTION]->(prog_descriptions:Programmatic_Description)
        OPTIONAL MATCH (wmk:Feature_Watermark)-[:BELONG_TO_FEATURE]->(feat:Feature)
        RETURN feat, description, fg,
        collect(distinct wmk) AS wmk_records,
        collect(distinct db) AS availability_records,
        collect(distinct owner) AS owner_records,
        collect(distinct `tag`) AS tag_records,
        collect(distinct badge) AS badge_records,
        collect(distinct prog_descriptions) AS prog_descriptions
        """))

        results = self._execute_query(
            query=feature_query.render(feature_key=feature_key),
            param_dict={})[0]
        data = results.get('data', None)

        if not data:
            raise NotFoundException(
                'Feature with key {} does not exist'.format(feature_key))

        (i_feature, i_description, i_feature_group, i_wmk_records, i_availability_records,
            i_owner_records, i_tag_records, i_badge_records, i_prog_descriptions) = \
                self._get_result_column_indexes(results, (
                    'feat', 'description', 'fg', 'wmk_records', 'availability_records',
                    'owner_records', 'tag_records', 'badge_records', 'prog_descriptions'))

        record, meta = data[0]['row'], data[0]['meta']
        watermarks = self._create_feature_watermarks(
            wmk_records=record[i_wmk_records], wmk_meta=meta[i_wmk_records])

        availability_records = [
            db['Database.name'] for db in record[i_availability_records]
        ]

        description = None
        if record[i_description] is not None:
            description = record[i_description].get('Description.description',
                                                    None)

        programmatic_descriptions = self._create_programmatic_descriptions(
            record[i_prog_descriptions])

        owners = self._create_owners(record[i_owner_records])

        tags = []
        for i, tag in enumerate(record[i_tag_records]):
            tag_result = Tag(tag_name=meta[i_tag_records][i].get('id', None),
                             tag_type=tag.get('Tag.tag_type', None))
            tags.append(tag_result)

        feature_node, feature_node_meta = record[i_feature], meta[i_feature]

        feature_group = record[i_feature_group]

        badges = self._make_badges(record[i_badge_records],
                                   meta[i_badge_records])

        return {
            'key':
            feature_node_meta.get('id'),
            'name':
            feature_node.get('Feature.name'),
            'version':
            feature_node.get('Feature.version'),
            'feature_group':
            feature_group.get('Feature_Group.name'),
            'data_type':
            feature_node.get('Feature.data_type'),
            'entity':
            feature_node.get('Feature.entity'),
            'description':
            description,
            'programmatic_descriptions':
            programmatic_descriptions,
            'last_updated_timestamp':
            int(feature_node.get('Feature.last_updated_timestamp'))
            if feature_node.get('Feature.last_updated_timestamp') else None,
            'created_timestamp':
            int(feature_node.get('created_timestamp'))
            if feature_node.get('created_timestamp') else None,
            'watermarks':
            watermarks,
            'availability':
            availability_records,
            'tags':
            tags,
            'badges':
            badges,
            'owners':
            owners,
            'status':
            feature_node.get('Feature.status', None)
        }

    def get_feature(self, *, feature_uri: str) -> Feature:
        """
        :param feature_uri: uniquely identifying key for a feature node
        :return: a Feature object
        """
        feature_metadata = self._exec_feature_query(feature_key=feature_uri)

        feature = Feature(
            key=feature_metadata['key'],
            name=feature_metadata['name'],
            version=feature_metadata['version'],
            status=feature_metadata['status'],
            feature_group=feature_metadata['feature_group'],
            entity=feature_metadata['entity'],
            data_type=feature_metadata['data_type'],
            availability=feature_metadata['availability'],
            description=feature_metadata['description'],
            owners=feature_metadata['owners'],
            badges=feature_metadata['badges'],
            tags=feature_metadata['tags'],
            programmatic_descriptions=feature_metadata[
                'programmatic_descriptions'],
            last_updated_timestamp=feature_metadata['last_updated_timestamp'],
            created_timestamp=feature_metadata['created_timestamp'],
            watermarks=feature_metadata['watermarks'])
        return feature

    def get_resource_generation_code(
            self, *, uri: str, resource_type: ResourceType) -> GenerationCode:
        """
        Executes query to get query nodes associated with resource
        """

        query = Template(
            textwrap.dedent("""
        MATCH (feat:`{{ resource_type }}`)
        WHERE id(feat) == "{{ uri }}"
        OPTIONAL MATCH (q:Feature_Generation_Code)-[:GENERATION_CODE_OF]->(feat:`{{ resource_type }}`)
        RETURN q AS query_records
        """))
        records = self._execute_query(query=query.render(
            resource_type=resource_type.name, uri=uri),
                                      param_dict={})[0]
        data = records.get('data', None)
        if not data:
            raise NotFoundException(
                'Generation code for id {} does not exist'.format(id))

        i_query_records = self._get_result_column_index(
            records, 'query_records')
        record, meta = data[0]['row'], data[0]['meta']
        if meta[i_query_records] is None or record[i_query_records] is None:
            raise NotFoundException(
                'Generation code for id {} does not exist'.format(id))

        key = meta[i_query_records].get('id', None)
        if key is None:
            raise NotFoundException(
                'Generation code for id {} does not exist'.format(id))
        text = record[i_query_records].get(
            'Feature_Generation_Code.text',
            None) if record[i_query_records] else None
        source = record[i_query_records].get(
            'Feature_Generation_Code.source',
            None) if record[i_query_records] else None

        return GenerationCode(key=key, text=text, source=source)
