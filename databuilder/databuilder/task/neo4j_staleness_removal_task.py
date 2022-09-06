# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import textwrap
import time
from typing import (
    Any, Dict, Iterable, Union,
)

import neo4j
from neo4j import GraphDatabase
from neo4j.api import (
    SECURITY_TYPE_SECURE, SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, parse_neo4j_uri,
)
from pyhocon import ConfigFactory, ConfigTree

from databuilder import Scoped
from databuilder.publisher.neo4j_csv_publisher import JOB_PUBLISH_TAG
from databuilder.task.base_task import Task

# A end point for Neo4j e.g: bolt://localhost:9999
NEO4J_END_POINT_KEY = 'neo4j_endpoint'
NEO4J_MAX_CONN_LIFE_TIME_SEC = 'neo4j_max_conn_life_time_sec'
NEO4J_USER = 'neo4j_user'
NEO4J_PASSWORD = 'neo4j_password'
# in Neo4j (v4.0+), we can create and use more than one active database at the same time
NEO4J_DATABASE_NAME = 'neo4j_database'
NEO4J_ENCRYPTED = 'neo4j_encrypted'
"""NEO4J_ENCRYPTED is a boolean indicating whether to use SSL/TLS when connecting."""
NEO4J_VALIDATE_SSL = 'neo4j_validate_ssl'
"""NEO4J_VALIDATE_SSL is a boolean indicating whether to validate the server's SSL/TLS cert against system CAs."""
TARGET_NODES = "target_nodes"
TARGET_RELATIONS = "target_relations"
BATCH_SIZE = "batch_size"
DRY_RUN = "dry_run"
# Staleness max percentage. Safety net to prevent majority of data being deleted.
STALENESS_MAX_PCT = "staleness_max_pct"
# Staleness max percentage per LABEL/TYPE. Safety net to prevent majority of data being deleted.
STALENESS_PCT_MAX_DICT = "staleness_max_pct_dict"
# Using this milliseconds and published timestamp to determine staleness
MS_TO_EXPIRE = "milliseconds_to_expire"
MIN_MS_TO_EXPIRE = "minimum_milliseconds_to_expire"
RETAIN_DATA_WITH_NO_PUBLISHER_METADATA = "retain_data_with_no_publisher_metadata"

DEFAULT_CONFIG = ConfigFactory.from_dict({BATCH_SIZE: 100,
                                          NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
                                          NEO4J_DATABASE_NAME: neo4j.DEFAULT_DATABASE,
                                          STALENESS_MAX_PCT: 5,
                                          TARGET_NODES: [],
                                          TARGET_RELATIONS: [],
                                          STALENESS_PCT_MAX_DICT: {},
                                          MIN_MS_TO_EXPIRE: 86400000,
                                          RETAIN_DATA_WITH_NO_PUBLISHER_METADATA: False,
                                          DRY_RUN: False})

LOGGER = logging.getLogger(__name__)

MARKER_VAR_NAME = 'marker'


class TargetWithCondition:
    def __init__(self, target_type: str, condition: str) -> None:
        self.target_type = target_type
        self.condition = condition


class Neo4jStalenessRemovalTask(Task):
    """
    A Specific task that is to remove stale nodes and relations in Neo4j.
    It will use "published_tag" attribute assigned from Neo4jCsvPublisher and if "published_tag" is different from
    the one it is getting it from the config, it will regard the node/relation as stale.
    Not all resource is being published by Neo4jCsvPublisher and you can only set specific LABEL of the node or TYPE
    of relation to perform this deletion.

    """

    delete_stale_nodes_statement = textwrap.dedent("""
        MATCH (target:{{type}})
        WHERE {staleness_condition}{{extra_condition}}
        WITH target LIMIT $batch_size
        DETACH DELETE (target)
        RETURN count(*) as count
        """)
    delete_stale_relations_statement = textwrap.dedent("""
        MATCH (start_node)-[target:{{type}}]-(end_node)
        WHERE {staleness_condition}{{extra_condition}}
        WITH target LIMIT $batch_size
        DELETE target
        RETURN count(*) as count
        """)
    validate_node_staleness_statement = textwrap.dedent("""
        MATCH (target:{{type}})
        WHERE {staleness_condition}{{extra_condition}}
        RETURN count(*) as count
        """)
    validate_relation_staleness_statement = textwrap.dedent("""
        MATCH (start_node)-[target:{{type}}]-(end_node)
        WHERE {staleness_condition}{{extra_condition}}
        RETURN count(*) as count
        """)

    def __init__(self) -> None:
        pass

    def get_scope(self) -> str:
        return 'task.remove_stale_data'

    def init(self, conf: ConfigTree) -> None:
        conf = Scoped.get_scoped_conf(conf, self.get_scope()) \
            .with_fallback(conf) \
            .with_fallback(DEFAULT_CONFIG)
        self.target_nodes = set(conf.get_list(TARGET_NODES))
        self.target_relations = set(conf.get_list(TARGET_RELATIONS))
        self.batch_size = conf.get_int(BATCH_SIZE)
        self.dry_run = conf.get_bool(DRY_RUN)
        self.staleness_pct = conf.get_int(STALENESS_MAX_PCT)
        self.staleness_pct_dict = conf.get(STALENESS_PCT_MAX_DICT)
        self.retain_data_with_no_publisher_metadata = conf.get_bool(RETAIN_DATA_WITH_NO_PUBLISHER_METADATA)

        if JOB_PUBLISH_TAG in conf and MS_TO_EXPIRE in conf:
            raise Exception(f'Cannot have both {JOB_PUBLISH_TAG} and {MS_TO_EXPIRE} in job config')

        self.ms_to_expire = None
        if MS_TO_EXPIRE in conf:
            self.ms_to_expire = conf.get_int(MS_TO_EXPIRE)
            if self.ms_to_expire < conf.get_int(MIN_MS_TO_EXPIRE):
                raise Exception(f'{MS_TO_EXPIRE} is too small')
            self.marker = self.ms_to_expire
        else:
            self.marker = conf.get_string(JOB_PUBLISH_TAG)

        uri = conf.get_string(NEO4J_END_POINT_KEY)
        driver_args = {
            'uri': uri,
            'max_connection_lifetime': conf.get_int(NEO4J_MAX_CONN_LIFE_TIME_SEC),
            'auth': (conf.get_string(NEO4J_USER), conf.get_string(NEO4J_PASSWORD)),
        }

        # if URI scheme not secure set `trust`` and `encrypted` to default values
        # https://neo4j.com/docs/api/python-driver/current/api.html#uri
        _, security_type, _ = parse_neo4j_uri(uri=uri)
        if security_type not in [SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, SECURITY_TYPE_SECURE]:
            default_security_conf = {'trust': neo4j.TRUST_ALL_CERTIFICATES, 'encrypted': True}
            driver_args.update(default_security_conf)

        # if NEO4J_VALIDATE_SSL or NEO4J_ENCRYPTED are set in config pass them to the driver
        validate_ssl_conf = conf.get(NEO4J_VALIDATE_SSL, None)
        encrypted_conf = conf.get(NEO4J_ENCRYPTED, None)
        if validate_ssl_conf is not None:
            driver_args['trust'] = neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES if validate_ssl_conf \
                else neo4j.TRUST_ALL_CERTIFICATES
        if encrypted_conf is not None:
            driver_args['encrypted'] = encrypted_conf

        self._driver = GraphDatabase.driver(**driver_args)

        self.db_name = conf.get(NEO4J_DATABASE_NAME)

    def run(self) -> None:
        """
        First, performs a safety check to make sure this operation would not delete more than a threshold where
        default threshold is 5%. Once it passes a safety check, it will first delete stale nodes, and then stale
        relations.
        :return:
        """
        self.validate()
        self._delete_stale_nodes()
        self._delete_stale_relations()

    def validate(self) -> None:
        """
        Validation method. Focused on limit the risk on deleting nodes and relations.
         - Check if deleted nodes will be within 10% of total nodes.
        :return:
        """
        self._validate_node_staleness_pct()
        self._validate_relation_staleness_pct()

    def _delete_stale_nodes(self) -> None:
        self._batch_delete(statement=self._decorate_staleness(self.delete_stale_nodes_statement),
                           targets=self.target_nodes)

    def _decorate_staleness(self,
                            statement: str
                            ) -> str:
        """
        Append where clause to the Cypher statement depends on which field to be used to expire stale data.
        :param statement:
        :return:
        """
        if self.ms_to_expire:
            condition = f"""target.publisher_last_updated_epoch_ms < (timestamp() - ${MARKER_VAR_NAME})"""
            if not self.retain_data_with_no_publisher_metadata:
                null_check = "EXISTS(target.publisher_last_updated_epoch_ms)"
                condition = f"""{condition}\nOR NOT {null_check}"""
            condition = f"""({condition})"""
            return statement.format(staleness_condition=condition)

        condition = f"""target.published_tag < ${MARKER_VAR_NAME}"""
        if not self.retain_data_with_no_publisher_metadata:
            null_check = "EXISTS(target.published_tag)"
            condition = f"""{condition}\nOR NOT {null_check}"""
        condition = f"""({condition})"""
        return statement.format(staleness_condition=condition)

    def _delete_stale_relations(self) -> None:
        self._batch_delete(statement=self._decorate_staleness(self.delete_stale_relations_statement),
                           targets=self.target_relations)

    def _batch_delete(self,
                      statement: str,
                      targets: Union[Iterable[str], Iterable[TargetWithCondition]]
                      ) -> None:
        """
        Performing huge amount of deletion could degrade Neo4j performance. Therefore, it's taking batch deletion here.
        :param statement:
        :param targets:
        :return:
        """
        for t in targets:
            if isinstance(t, TargetWithCondition):
                target_type = t.target_type
                extra_condition = ' AND ' + t.condition
            else:
                target_type = t
                extra_condition = ''

            LOGGER.info('Deleting stale data of %s with batch size %i', target_type, self.batch_size)
            total_count = 0
            while True:
                results = self._execute_cypher_query(statement=statement.format(type=target_type,
                                                                                extra_condition=extra_condition),
                                                     param_dict={'batch_size': self.batch_size,
                                                                 MARKER_VAR_NAME: self.marker},
                                                     dry_run=self.dry_run)
                record = next(iter(results), None)
                count = record['count'] if record else 0
                total_count = total_count + count
                if count == 0:
                    break
            LOGGER.info('Deleted %i stale data of %s', total_count, target_type)

    def _validate_staleness_pct(self,
                                total_record_count: int,
                                stale_record_count: int,
                                target_type: str
                                ) -> None:
        if total_record_count == 0 or stale_record_count == 0:
            return

        stale_pct = stale_record_count * 100 / total_record_count

        threshold = self.staleness_pct_dict.get(target_type, self.staleness_pct)
        if stale_pct >= threshold:
            raise Exception(f'Staleness percentage of {target_type} is {stale_pct} %. '
                            f'Stopping due to over threshold {threshold} %')

    def _validate_node_staleness_pct(self) -> None:
        total_nodes_statement = textwrap.dedent(
            self.validate_node_staleness_statement.format(staleness_condition='true'))
        stale_nodes_statement = textwrap.dedent(
            self._decorate_staleness(self.validate_node_staleness_statement))

        for t in self.target_nodes:
            if isinstance(t, TargetWithCondition):
                target_type = t.target_type
                extra_condition = ' AND ' + t.condition
            else:
                target_type = t
                extra_condition = ''

            total_records = self._execute_cypher_query(
                statement=total_nodes_statement.format(type=target_type,
                                                       extra_condition=extra_condition))
            stale_records = self._execute_cypher_query(
                statement=stale_nodes_statement.format(type=target_type,
                                                       extra_condition=extra_condition),
                param_dict={MARKER_VAR_NAME: self.marker})

            total_record_value = next(iter(total_records), None)
            stale_record_value = next(iter(stale_records), None)
            self._validate_staleness_pct(total_record_count=total_record_value['count'] if total_record_value else 0,
                                         stale_record_count=stale_record_value['count'] if stale_record_value else 0,
                                         target_type=target_type)

    def _validate_relation_staleness_pct(self) -> None:
        total_relations_statement = textwrap.dedent(
            self.validate_relation_staleness_statement.format(staleness_condition='true'))
        stale_relations_statement = textwrap.dedent(
            self._decorate_staleness(self.validate_relation_staleness_statement))

        for t in self.target_relations:
            if isinstance(t, TargetWithCondition):
                target_type = t.target_type
                extra_condition = ' AND ' + t.condition
            else:
                target_type = t
                extra_condition = ''

            total_records = self._execute_cypher_query(
                statement=total_relations_statement.format(type=target_type,
                                                           extra_condition=extra_condition))
            stale_records = self._execute_cypher_query(
                statement=stale_relations_statement.format(type=target_type,
                                                           extra_condition=extra_condition),
                param_dict={MARKER_VAR_NAME: self.marker})

            total_record_value = next(iter(total_records), None)
            stale_record_value = next(iter(stale_records), None)
            self._validate_staleness_pct(total_record_count=total_record_value['count'] if total_record_value else 0,
                                         stale_record_count=stale_record_value['count'] if stale_record_value else 0,
                                         target_type=target_type)

    def _execute_cypher_query(self,
                              statement: str,
                              param_dict: Dict[str, Any] = {},
                              dry_run: bool = False
                              ) -> Iterable[Dict[str, Any]]:
        LOGGER.info('Executing Cypher query: %s with params %s: ', statement, param_dict)

        if dry_run:
            LOGGER.info('Skipping for it is a dryrun')
            return []

        start = time.time()
        try:
            with self._driver.session(database=self.db_name) as session:
                result = session.run(statement, **param_dict)
                return [record for record in result]

        finally:
            LOGGER.debug('Cypher query execution elapsed for %i seconds', time.time() - start)
