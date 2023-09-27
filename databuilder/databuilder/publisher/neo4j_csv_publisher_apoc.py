# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import csv
import ctypes
import logging
import time
from io import open
from os import listdir
from os.path import isfile, join
from typing import List, Set

import neo4j
import pandas
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
from pyhocon import ConfigFactory, ConfigTree

from databuilder.publisher.base_publisher import Publisher
from databuilder.publisher.neo4j_preprocessor import NoopRelationPreprocessor

# Setting field_size_limit to solve the error below
# _csv.Error: field larger than field limit (131072)
# https://stackoverflow.com/a/54517228/5972935
csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

# Use the Neo4J APOC library for batch processing. Using this publisher
# requires APOC to be installed as a plugin in your Neo4J database.
# Notes on this implementation:
#   - Did not re-implement self._relation_preprocessor, not sure what this is.
#   - Zero performance tuning or query optimization - picked arbitrary numbers for
#     batch sizes. Goal was functionally correct APOC based cypher queries in first
#     iteration that can be tuned over time.

# Config keys
# A directory that contains CSV files for nodes
NODE_FILES_DIR = 'node_files_directory'
# A directory that contains CSV files for relationships
RELATION_FILES_DIR = 'relation_files_directory'
# A end point for Neo4j e.g: bolt://localhost:9999
NEO4J_END_POINT_KEY = 'neo4j_endpoint'
# How many
NEO4J_TRANSACTION_SIZE = 'neo4j_transaction_size'
# A transaction size that determines how often it commits.
NEO4J_BATCH_SIZE = 'neo4j_batch_size'
# A progress report frequency that determines how often it report the progress.
NEO4J_PROGRESS_REPORT_FREQUENCY = 'neo4j_progress_report_frequency'
# A boolean flag to make it fail if relationship is not created
NEO4J_RELATIONSHIP_CREATION_CONFIRM = 'neo4j_relationship_creation_confirm'

NEO4J_MAX_CONN_LIFE_TIME_SEC = 'neo4j_max_conn_life_time_sec'

# list of nodes that are create only, and not updated if match exists
NEO4J_CREATE_ONLY_NODES = 'neo4j_create_only_nodes'

# list of node labels that could attempt to be accessed simultaneously
NEO4J_DEADLOCK_NODE_LABELS = 'neo4j_deadlock_node_labels'

NEO4J_USER = 'neo4j_user'
NEO4J_PASSWORD = 'neo4j_password'
NEO4J_ENCRYPTED = 'neo4j_encrypted'
"""NEO4J_ENCRYPTED is a boolean indicating whether to use SSL/TLS when connecting."""
NEO4J_VALIDATE_SSL = 'neo4j_validate_ssl'
"""NEO4J_VALIDATE_SSL is a boolean indicating whether to validate the server's SSL/TLS cert against system CAs."""

# This will be used to provide unique tag to the node and relationship
JOB_PUBLISH_TAG = 'job_publish_tag'

# Neo4j property name for published tag
PUBLISHED_TAG_PROPERTY_NAME = 'published_tag'

# Neo4j property name for last updated timestamp
LAST_UPDATED_EPOCH_MS = 'publisher_last_updated_epoch_ms'

RELATION_PREPROCESSOR = 'relation_preprocessor'

# CSV HEADER
# A header with this suffix will be pass to Neo4j statement without quote
UNQUOTED_SUFFIX = ':UNQUOTED'
# A header for Node label
NODE_LABEL_KEY = 'LABEL'
# A header for Node key
NODE_KEY_KEY = 'KEY'
# Required columns for Node
NODE_REQUIRED_KEYS = {NODE_LABEL_KEY, NODE_KEY_KEY}

# Relationship relates two nodes together
# Start node label
RELATION_START_LABEL = 'START_LABEL'
# Start node key
RELATION_START_KEY = 'START_KEY'
# End node label
RELATION_END_LABEL = 'END_LABEL'
# Node node key
RELATION_END_KEY = 'END_KEY'
# Type for relationship (Start Node)->(End Node)
RELATION_TYPE = 'TYPE'
# Type for reverse relationship (End Node)->(Start Node)
RELATION_REVERSE_TYPE = 'REVERSE_TYPE'
# Required columns for Relationship
RELATION_REQUIRED_KEYS = {RELATION_START_LABEL, RELATION_START_KEY,
                          RELATION_END_LABEL, RELATION_END_KEY,
                          RELATION_TYPE, RELATION_REVERSE_TYPE}

DEFAULT_CONFIG = ConfigFactory.from_dict({NEO4J_TRANSACTION_SIZE: 10000,
                                          NEO4J_BATCH_SIZE: 500,
                                          NEO4J_PROGRESS_REPORT_FREQUENCY: 500,
                                          NEO4J_RELATIONSHIP_CREATION_CONFIRM: False,
                                          NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
                                          NEO4J_ENCRYPTED: True,
                                          NEO4J_VALIDATE_SSL: False,
                                          RELATION_PREPROCESSOR: NoopRelationPreprocessor()})

# transient error retries and sleep time
RETRIES_NUMBER = 5
SLEEP_TIME = 2

LOGGER = logging.getLogger(__name__)


class Neo4jCsvPublisherApoc(Publisher):
    """
    A Publisher takes two folders for input and publishes to Neo4j.
    One folder will contain CSV file(s) for Node where the other folder will contain CSV file(s) for Relationship.

    Neo4j follows Label Node properties Graph and more information about this is in:
    https://neo4j.com/docs/developer-manual/current/introduction/graphdb-concepts/
    """

    def __init__(self) -> None:
        super(Neo4jCsvPublisherApoc, self).__init__()

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(DEFAULT_CONFIG)

        self._count: int = 0
        self._progress_report_frequency = conf.get_int(NEO4J_PROGRESS_REPORT_FREQUENCY)
        self._node_files = self._list_files(conf, NODE_FILES_DIR)
        self._node_files_iter = iter(self._node_files)

        self._relation_files = self._list_files(conf, RELATION_FILES_DIR)
        self._relation_files_iter = iter(self._relation_files)

        trust = neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES if conf.get_bool(NEO4J_VALIDATE_SSL) \
            else neo4j.TRUST_ALL_CERTIFICATES
        driver_args = {
            'uri': conf.get_string(NEO4J_END_POINT_KEY),
            'max_connection_lifetime': conf.get_int(NEO4J_MAX_CONN_LIFE_TIME_SEC),
            'auth': (conf.get_string(NEO4J_USER), conf.get_string(NEO4J_PASSWORD)),
            'encrypted': conf.get_bool(NEO4J_ENCRYPTED),
            'trust': trust,
        }
        self._driver = \
            GraphDatabase.driver(**driver_args)
        self._batch_size = conf.get_int(NEO4J_BATCH_SIZE)
        self._transaction_size = conf.get_int(NEO4J_TRANSACTION_SIZE)
        self._confirm_rel_created = conf.get_bool(NEO4J_RELATIONSHIP_CREATION_CONFIRM)

        # config is list of node label.
        # When set, this list specifies a list of nodes that shouldn't be updated, if exists
        self.create_only_nodes = set(conf.get_list(NEO4J_CREATE_ONLY_NODES, default=[]))
        self.deadlock_node_labels = set(conf.get_list(NEO4J_DEADLOCK_NODE_LABELS, default=[]))
        self.labels: Set[str] = set()
        self.publish_tag: str = conf.get_string(JOB_PUBLISH_TAG)
        if not self.publish_tag:
            raise Exception(f'{JOB_PUBLISH_TAG} should not be empty')

        self._relation_preprocessor = conf.get(RELATION_PREPROCESSOR)

        LOGGER.info('Publishing Node csv files %s, and Relation CSV files %s', self._node_files, self._relation_files)

    def _list_files(self, conf: ConfigTree, path_key: str) -> List[str]:
        """
        List files from directory
        :param conf:
        :param path_key:
        :return: List of file paths
        """
        if path_key not in conf:
            return []

        path = conf.get_string(path_key)
        return [join(path, f) for f in listdir(path) if isfile(join(path, f))]

    def publish_impl(self) -> None:  # noqa: C901
        """
        Publishes Nodes first and then Relations
        :return:
        """
        start = time.time()

        LOGGER.info('Creating indices using Node files: %s', self._node_files)
        for node_file in self._node_files:
            self._create_indices(node_file=node_file)

        LOGGER.info('Publishing Node files: %s', self._node_files)
        while True:
            try:
                node_file = next(self._node_files_iter)
                LOGGER.info('_publish_node(%s)', node_file)
                quick = time.time()
                self._publish_node(node_file)
                LOGGER.info('Successfully published nodes. Elapsed: %i seconds', time.time() - quick)
            except StopIteration:
                break

        LOGGER.info('Publishing Relationship files: %s', self._relation_files)
        while True:
            try:
                relation_file = next(self._relation_files_iter)
                LOGGER.info('_publish_relation(%s)', relation_file)
                quick = time.time()
                self._publish_relation(relation_file)
                LOGGER.info('Successfully published relationships. Elapsed: %i seconds', time.time() - quick)
            except StopIteration:
                break

        # TODO: Add statsd support
        LOGGER.info('Successfully published all. Elapsed: %i seconds', time.time() - start)

    def get_scope(self) -> str:
        return 'publisher.neo4j'

    def _create_indices(self, node_file: str) -> None:
        """
        Go over the node file and try creating unique index
        :param node_file:
        :return:
        """
        LOGGER.info('Creating indices. (Existing indices will be ignored)')

        with open(node_file, 'r', encoding='utf8') as node_csv:
            for node_record in pandas.read_csv(node_csv, na_filter=False).to_dict(orient='records'):
                label = node_record[NODE_LABEL_KEY]
                if label not in self.labels:
                    self._try_create_index(label)
                    self.labels.add(label)

        LOGGER.info('Indices have been created.')

    def _chunker(self, seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    def _unquote(self, k) -> str:
        if k.endswith(UNQUOTED_SUFFIX):
            k = k[:-len(UNQUOTED_SUFFIX)]
        return k

    def _publish_node(self, node_file: str) -> None:
        """
        Iterate over the csv records of a file, each csv record transform to apoc.node.merge statement
        and will be executed.
        All nodes should have a unique key, and this method will try to create unique index on the LABEL when it sees
        first time within a job scope.
        Example of Cypher query executed by this method:
        CALL apoc.periodic.iterate(
            'UNWIND $rows AS row RETURN row',
            'CALL apoc.merge.node([row.label], {key:row.key}, row, row) YIELD node RETURN COUNT(*);',
            {batchSize: $batch_size, iterateList: True, parallel: False, params: { rows: $batch, tag: $publish_tag }}
        );
        :param node_file:
        :return:
        """
        df = pandas.read_csv(node_file, na_filter=False)
        df = df.rename(columns=self._unquote)  # Remove the UNQUOTED_SUFFIX+

        # Add these two columns so they are included in properties.
        df[PUBLISHED_TAG_PROPERTY_NAME] = self.publish_tag
        # TODO: Struggled to get timestamp() into the query string properly without quotes
        # so Neo4J could calculate the time - so this is a workaround. Ideally we can
        # figure out how to properly leverage timestamp().
        df[LAST_UPDATED_EPOCH_MS] = int(time.time() * 1e6)

        # Process in chunks so as not to overwhelm the neo4j java heap. In a production
        # grade Neo4J the heap is likely large enough to handle much larger batches
        chunks_total = len(df) // self._transaction_size
        chunks = self._chunker(df.to_dict(orient="records"), self._transaction_size)
        for idx, chunk in enumerate(chunks):
            LOGGER.info('Batch %i of %i...', idx, chunks_total)
            stmt = self.create_node_merge_statement(chunk)
            params = {
                'batch': chunk,
                'batch_size': self._batch_size,
                'publish_tag': self.publish_tag
            }
            self._execute_statement(stmt, params=params)

    def is_create_only_node(self, node_record: dict) -> bool:
        """
        Check if node can be updated
        :param node_record:
        :return:
        """
        if self.create_only_nodes:
            return node_record[NODE_LABEL_KEY] in self.create_only_nodes
        else:
            return False

    def create_node_merge_statement(self, node_records: dict = None,) -> str:
        """
        Creates node merge statement
        :param node_records:
        :return:
        """
        # apoc.periodic.iterate - https://neo4j.com/labs/apoc/4.2/overview/apoc.periodic/apoc.periodic.iterate/
        # There are lots of tuning parameters including support for parallelization and
        # batching options that can be explored.
        # Have not yet analyzed query plan caching, so there is likely additional speedup possible with
        # investigation.
        # TODO: check out https://neo4j.com/docs/cypher-manual/current/query-tuning/advanced-example/
        if self.is_create_only_node(node_records[0]):
            return """
                CALL apoc.periodic.iterate('UNWIND $rows AS row RETURN row', '
                    CALL apoc.merge.node([row.label], {key:row.key}, row,
                    {published_tag:$tag,publisher_last_updated_epoch_ms:timestamp()})
                    YIELD node RETURN COUNT(*);
                ',
                {batchSize: $batch_size}
                {iterateList: True}
                {parallel: False}
                {params: { rows: $batch, tag: $publish_tag }})
            """

        return """
            CALL apoc.periodic.iterate('UNWIND $rows AS row RETURN row', '
                CALL apoc.merge.node([row.label], {key:row.key}, row, row) YIELD node RETURN COUNT(*);
            ', {batchSize: $batch_size, iterateList: True, parallel: False, params: { rows: $batch }})
        """

    def _publish_relation(self, relation_file: str) -> None:
        """
        Creates relation between two nodes.
        (In Amundsen, all relation is bi-directional)

        Example of Cypher query executed by this method:
        CALL apoc.periodic.iterate('UNWIND $rows AS row RETURN row',
            'CALL apoc.merge.node([row.start_label], {key:row.start_key}) YIELD node AS n1
             CALL apoc.merge.node([row.end_label], {key:row.end_key}) YIELD node AS n2
             CALL apoc.merge.relationship(n1, row.type, {}, {{PROPS}}, n2, {{PROPS}}) YIELD rel AS r1
             CALL apoc.merge.relationship(n2, row.reverse_type, {}, {{PROPS}}, n1, {{PROPS}}) YIELD rel AS r2
             RETURN n1.key, n2.key',
            {batchSize: $batch_size, parallel: False, params: { rows: $batch, tag: $publish_tag }}
        )
        :param relation_file:
        :return:
        """

        if self._relation_preprocessor.is_perform_preprocess():
            LOGGER.info('Pre-processing relation with %s', self._relation_preprocessor)

            count = 0
            with open(relation_file, 'r', encoding='utf8') as relation_csv:
                for rel_record in pandas.read_csv(relation_csv, na_filter=False).to_dict(orient="records"):
                    # TODO not sure if deadlock on badge node arises in preporcessing or not
                    stmt, params = self._relation_preprocessor.preprocess_cypher(
                        start_label=rel_record[RELATION_START_LABEL],
                        end_label=rel_record[RELATION_END_LABEL],
                        start_key=rel_record[RELATION_START_KEY],
                        end_key=rel_record[RELATION_END_KEY],
                        relation=rel_record[RELATION_TYPE],
                        reverse_relation=rel_record[RELATION_REVERSE_TYPE])

                    if stmt:
                        self._execute_statement(stmt, params=params)
                        count += 1

            LOGGER.info('Executed pre-processing Cypher statement %i times', count)

        df = pandas.read_csv(relation_file, na_filter=False)
        df = df.rename(columns=self._unquote)  # remove the UNQUOTED_SUFFIX+

        # Add these two columns so they are included in properties.
        df[PUBLISHED_TAG_PROPERTY_NAME] = self.publish_tag
        # TODO: Struggled to get timestamp() into the query string properly without quotes
        # so Neo4J could calculate the time - so this is a workaround. Ideally we can
        # figure out how to properly leverage timestamp().
        df[LAST_UPDATED_EPOCH_MS] = int(time.time() * 1e6)

        # Process in chunks so as not to overwhelm the neo4j java heap. In a production
        # grade Neo4J the heap is likely large enough to handle much larger batches
        chunks_total = len(df) // self._transaction_size
        chunks = self._chunker(df.to_dict(orient="records"), self._transaction_size)
        for idx, chunk in enumerate(chunks):
            LOGGER.info('Batch %i of %i...', idx, chunks_total)
            stmt = self.create_relationship_merge_statement()
            params = {
                'batch': chunk,
                'batch_size': self._batch_size,
                'publish_tag': self.publish_tag
            }
            self._execute_statement(stmt, params=params,
                                    expect_result=self._confirm_rel_created)

    def create_relationship_merge_statement(self) -> str:
        """
        Creates relationship merge statement
        :return:
        """
        # apoc.periodic.iterate - https://neo4j.com/labs/apoc/4.2/overview/apoc.periodic/apoc.periodic.iterate/
        # There are lots of tuning parameters including support for parallelization and
        # batching options that can be explored.
        # Have not yet analyzed query plan caching, so there is likely additional speedup possible with
        # investigation.
        # TODO: check out https://neo4j.com/docs/cypher-manual/current/query-tuning/advanced-example/
        return """
            CALL apoc.periodic.iterate('UNWIND $rows AS row RETURN row', '
                CALL apoc.merge.node([row.start_label], {key:row.start_key}) YIELD node AS n1
                CALL apoc.merge.node([row.end_label], {key:row.end_key}) YIELD node AS n2
                CALL apoc.merge.relationship(n1, row.type, {},
                    {published_tag:$tag,publisher_last_updated_epoch_ms:timestamp()}, n2,
                    {published_tag:$tag,publisher_last_updated_epoch_ms:timestamp()}) YIELD rel AS r1
                CALL apoc.merge.relationship(n2, row.reverse_type, {},
                    {published_tag:$tag,publisher_last_updated_epoch_ms:timestamp()}, n1,
                    {published_tag:$tag,publisher_last_updated_epoch_ms:timestamp()}) YIELD rel AS r2
                RETURN n1.key, n2.key
            ', {batchSize: $batch_size, parallel: False, params: { rows: $batch, tag: $publish_tag }})
        """

    def _execute_statement(self,
                           stmt: str,
                           params: dict = None,
                           expect_result: bool = False) -> None:
        """
        Executes statement against Neo4j. If execution fails, it rollsback and raise exception.
        If 'expect_result' flag is True, it confirms if result object is not null.
        :param stmt:
        :param params:
        :param expect_result: By having this True, it will validate if result object is not None.
        :return:
        """
        with self._driver.session() as session:
            try:
                LOGGER.debug('Executing statement: %s with params %s', stmt, params)

                result = session.run(str(stmt).encode('utf-8', 'ignore'), parameters=params)

                if expect_result and not result.single():
                    raise RuntimeError(f'Failed to executed statement: {stmt}')

            except Exception as e:
                LOGGER.exception('Failed to execute Cypher query')
                raise e

    def _try_create_index(self, label: str) -> None:
        """
        For any label seen first time for this publisher it will try to create unique index.
        Neo4j ignores a second creation in 3.x, but raises an error in 4.x.
        :param label:
        :return:
        """
        # TODO: apoc.schema.assert may help here for handling neo4j 3.x and 4.x
        stmt = """
            CREATE CONSTRAINT ON (node:label) ASSERT node.key IS UNIQUE
        """

        LOGGER.info(f'Trying to create index for label {label} if not exist: {stmt}')
        with self._driver.session() as session:
            try:
                session.run(str(stmt).encode('utf-8', 'ignore'), parameters={
                    'label': label
                })
            except Neo4jError as e:
                if 'An equivalent constraint already exists' not in e.__str__():
                    raise
                # Else, swallow the exception, to make this function idempotent.
