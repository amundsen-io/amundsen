# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import csv
import ctypes
import logging
import time
from io import open
from os import listdir
from os.path import isfile, join
from typing import (
    Dict, List, Set,
)

import neo4j
import pandas
from jinja2 import Template
from neo4j import GraphDatabase, Transaction
from neo4j.api import (
    SECURITY_TYPE_SECURE, SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, parse_neo4j_uri,
)
from neo4j.exceptions import Neo4jError, TransientError
from pyhocon import ConfigFactory, ConfigTree

from databuilder.publisher.base_publisher import Publisher
from databuilder.publisher.neo4j_preprocessor import NoopRelationPreprocessor
from databuilder.publisher.publisher_config_constants import (
    Neo4jCsvPublisherConfigs, PublishBehaviorConfigs, PublisherConfigs,
)

# Setting field_size_limit to solve the error below
# _csv.Error: field larger than field limit (131072)
# https://stackoverflow.com/a/54517228/5972935
csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

# Config keys
# A directory that contains CSV files for nodes
NODE_FILES_DIR = PublisherConfigs.NODE_FILES_DIR
# A directory that contains CSV files for relationships
RELATION_FILES_DIR = PublisherConfigs.RELATION_FILES_DIR
# A end point for Neo4j e.g: bolt://localhost:9999
NEO4J_END_POINT_KEY = Neo4jCsvPublisherConfigs.NEO4J_END_POINT_KEY
# A transaction size that determines how often it commits.
NEO4J_TRANSACTION_SIZE = Neo4jCsvPublisherConfigs.NEO4J_TRANSACTION_SIZE
# A progress report frequency that determines how often it report the progress.
NEO4J_PROGRESS_REPORT_FREQUENCY = 'neo4j_progress_report_frequency'
# A boolean flag to make it fail if relationship is not created
NEO4J_RELATIONSHIP_CREATION_CONFIRM = 'neo4j_relationship_creation_confirm'

NEO4J_MAX_CONN_LIFE_TIME_SEC = Neo4jCsvPublisherConfigs.NEO4J_MAX_CONN_LIFE_TIME_SEC

# list of nodes that are create only, and not updated if match exists
NEO4J_CREATE_ONLY_NODES = Neo4jCsvPublisherConfigs.NEO4J_CREATE_ONLY_NODES

# list of node labels that could attempt to be accessed simultaneously
NEO4J_DEADLOCK_NODE_LABELS = 'neo4j_deadlock_node_labels'

NEO4J_USER = Neo4jCsvPublisherConfigs.NEO4J_USER
NEO4J_PASSWORD = Neo4jCsvPublisherConfigs.NEO4J_PASSWORD
# in Neo4j (v4.0+), we can create and use more than one active database at the same time
NEO4J_DATABASE_NAME = Neo4jCsvPublisherConfigs.NEO4J_DATABASE_NAME

# NEO4J_ENCRYPTED is a boolean indicating whether to use SSL/TLS when connecting
NEO4J_ENCRYPTED = Neo4jCsvPublisherConfigs.NEO4J_ENCRYPTED
# NEO4J_VALIDATE_SSL is a boolean indicating whether to validate the server's SSL/TLS
# cert against system CAs
NEO4J_VALIDATE_SSL = Neo4jCsvPublisherConfigs.NEO4J_VALIDATE_SSL

# This will be used to provide unique tag to the node and relationship
JOB_PUBLISH_TAG = PublisherConfigs.JOB_PUBLISH_TAG

# any additional fields that should be added to nodes and rels through config
ADDITIONAL_FIELDS = PublisherConfigs.ADDITIONAL_PUBLISHER_METADATA_FIELDS

# Neo4j property name for published tag
PUBLISHED_TAG_PROPERTY_NAME = PublisherConfigs.PUBLISHED_TAG_PROPERTY_NAME

# Neo4j property name for last updated timestamp
LAST_UPDATED_EPOCH_MS = PublisherConfigs.LAST_UPDATED_EPOCH_MS

# A boolean flag to indicate if publisher_metadata (e.g. published_tag,
# publisher_last_updated_epoch_ms)
# will be included as properties of the Neo4j nodes
ADD_PUBLISHER_METADATA = PublishBehaviorConfigs.ADD_PUBLISHER_METADATA

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

DEFAULT_CONFIG = ConfigFactory.from_dict({NEO4J_TRANSACTION_SIZE: 500,
                                          NEO4J_PROGRESS_REPORT_FREQUENCY: 500,
                                          NEO4J_RELATIONSHIP_CREATION_CONFIRM: False,
                                          NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
                                          NEO4J_DATABASE_NAME: neo4j.DEFAULT_DATABASE,
                                          ADDITIONAL_FIELDS: {},
                                          ADD_PUBLISHER_METADATA: True,
                                          RELATION_PREPROCESSOR: NoopRelationPreprocessor()})

# transient error retries and sleep time
RETRIES_NUMBER = 5
SLEEP_TIME = 2

LOGGER = logging.getLogger(__name__)


class Neo4jCsvPublisher(Publisher):
    """
    A Publisher takes two folders for input and publishes to Neo4j.
    One folder will contain CSV file(s) for Node where the other folder will contain CSV
    file(s) for Relationship.

    Neo4j follows Label Node properties Graph and more information about this is in:
    https://neo4j.com/docs/developer-manual/current/introduction/graphdb-concepts/

    #TODO User UNWIND batch operation for better performance
    """

    def __init__(self) -> None:
        super(Neo4jCsvPublisher, self).__init__()

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(DEFAULT_CONFIG)

        self._count: int = 0
        self._progress_report_frequency = conf.get_int(NEO4J_PROGRESS_REPORT_FREQUENCY)
        self._node_files = self._list_files(conf, NODE_FILES_DIR)
        self._node_files_iter = iter(self._node_files)

        self._relation_files = self._list_files(conf, RELATION_FILES_DIR)
        self._relation_files_iter = iter(self._relation_files)

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

        self._db_name = conf.get_string(NEO4J_DATABASE_NAME)
        self._session = self._driver.session(database=self._db_name)

        self._transaction_size = conf.get_int(NEO4J_TRANSACTION_SIZE)
        self._confirm_rel_created = conf.get_bool(NEO4J_RELATIONSHIP_CREATION_CONFIRM)

        # config is list of node label.
        # When set, this list specifies a list of nodes that shouldn't be updated, if exists
        self.create_only_nodes = set(conf.get_list(NEO4J_CREATE_ONLY_NODES, default=[]))
        self.deadlock_node_labels = set(conf.get_list(NEO4J_DEADLOCK_NODE_LABELS, default=[]))
        self.labels: Set[str] = set()
        self.publish_tag: str = conf.get_string(JOB_PUBLISH_TAG)
        self.additional_fields: Dict = conf.get(ADDITIONAL_FIELDS)
        self.add_publisher_metadata: bool = conf.get_bool(ADD_PUBLISHER_METADATA)
        if self.add_publisher_metadata and not self.publish_tag:
            raise Exception(f'{JOB_PUBLISH_TAG} should not be empty')

        self._relation_preprocessor = conf.get(RELATION_PREPROCESSOR)

        LOGGER.info('Publishing Node csv files %s, and Relation CSV files %s',
                    self._node_files,
                    self._relation_files)

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
        try:
            tx = self._session.begin_transaction()
            while True:
                try:
                    node_file = next(self._node_files_iter)
                    tx = self._publish_node(node_file, tx=tx)
                except StopIteration:
                    break

            LOGGER.info('Publishing Relationship files: %s', self._relation_files)
            while True:
                try:
                    relation_file = next(self._relation_files_iter)
                    tx = self._publish_relation(relation_file, tx=tx)
                except StopIteration:
                    break

            tx.commit()
            LOGGER.info('Committed total %i statements', self._count)

            # TODO: Add statsd support
            LOGGER.info('Successfully published. Elapsed: %i seconds', time.time() - start)
        except Exception as e:
            LOGGER.exception('Failed to publish. Rolling back.')
            if not tx.closed():
                tx.rollback()
            raise e

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
            for node_record in pandas.read_csv(node_csv,
                                               na_filter=False).to_dict(orient='records'):
                label = node_record[NODE_LABEL_KEY]
                if label not in self.labels:
                    self._try_create_index(label)
                    self.labels.add(label)

        LOGGER.info('Indices have been created.')

    def _publish_node(self, node_file: str, tx: Transaction) -> Transaction:
        """
        Iterate over the csv records of a file, each csv record transform to Merge statement
        and will be executed.
        All nodes should have a unique key, and this method will try to create unique index on
        the LABEL when it sees first time within a job scope.
        Example of Cypher query executed by this method:
        MERGE (col_test_id1:Column {key: 'presto://gold.test_schema1/test_table1/test_id1'})
        ON CREATE SET col_test_id1.name = 'test_id1',
                      col_test_id1.order_pos = 2,
                      col_test_id1.type = 'bigint'
        ON MATCH SET col_test_id1.name = 'test_id1',
                     col_test_id1.order_pos = 2,
                     col_test_id1.type = 'bigint'

        :param node_file:
        :return:
        """

        with open(node_file, 'r', encoding='utf8') as node_csv:
            for node_record in pandas.read_csv(node_csv,
                                               na_filter=False).to_dict(orient="records"):
                stmt = self.create_node_merge_statement(node_record=node_record)
                params = self._create_props_param(node_record)
                tx = self._execute_statement(stmt, tx, params)
        return tx

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

    def create_node_merge_statement(self, node_record: dict) -> str:
        """
        Creates node merge statement
        :param node_record:
        :return:
        """
        template = Template("""
            MERGE (node:{{ LABEL }} {key: $KEY})
            ON CREATE SET {{ PROP_BODY }}
            {% if update %} ON MATCH SET {{ PROP_BODY }} {% endif %}
        """)

        prop_body = self._create_props_body(node_record, NODE_REQUIRED_KEYS, 'node')

        return template.render(LABEL=node_record["LABEL"],
                               PROP_BODY=prop_body,
                               update=(not self.is_create_only_node(node_record)))

    def _publish_relation(self, relation_file: str, tx: Transaction) -> Transaction:
        """
        Creates relation between two nodes.
        (In Amundsen, all relation is bi-directional)

        Example of Cypher query executed by this method:
        MATCH (n1:Table {key: 'presto://gold.test_schema1/test_table1'}),
              (n2:Column {key: 'presto://gold.test_schema1/test_table1/test_col1'})
        MERGE (n1)-[r1:COLUMN]->(n2)-[r2:BELONG_TO_TABLE]->(n1)
        RETURN n1.key, n2.key

        :param relation_file:
        :return:
        """

        if self._relation_preprocessor.is_perform_preprocess():
            LOGGER.info('Pre-processing relation with %s', self._relation_preprocessor)

            count = 0
            with open(relation_file, 'r', encoding='utf8') as relation_csv:
                for rel_record in pandas.read_csv(relation_csv,
                                                  na_filter=False).to_dict(orient="records"):
                    # TODO not sure if deadlock on badge node arises in preporcessing or not
                    stmt, params = self._relation_preprocessor.preprocess_cypher(
                        start_label=rel_record[RELATION_START_LABEL],
                        end_label=rel_record[RELATION_END_LABEL],
                        start_key=rel_record[RELATION_START_KEY],
                        end_key=rel_record[RELATION_END_KEY],
                        relation=rel_record[RELATION_TYPE],
                        reverse_relation=rel_record[RELATION_REVERSE_TYPE])

                    if stmt:
                        tx = self._execute_statement(stmt, tx=tx, params=params)
                        count += 1

            LOGGER.info('Executed pre-processing Cypher statement %i times', count)

        with open(relation_file, 'r', encoding='utf8') as relation_csv:
            for rel_record in pandas.read_csv(relation_csv, na_filter=False).to_dict(orient="records"):
                exception_exists = True
                retries_for_exception = RETRIES_NUMBER
                while exception_exists and retries_for_exception > 0:
                    try:
                        stmt = self.create_relationship_merge_statement(rel_record=rel_record)
                        params = self._create_props_param(rel_record)
                        tx = self._execute_statement(stmt, tx, params,
                                                     expect_result=self._confirm_rel_created)
                        exception_exists = False
                    except TransientError as e:
                        if rel_record[RELATION_START_LABEL] in self.deadlock_node_labels \
                                or rel_record[RELATION_END_LABEL] in self.deadlock_node_labels:
                            time.sleep(SLEEP_TIME)
                            retries_for_exception -= 1
                        else:
                            raise e

        return tx

    def create_relationship_merge_statement(self, rel_record: dict) -> str:
        """
        Creates relationship merge statement
        :param rel_record:
        :return:
        """
        template = Template("""
            MATCH (n1:{{ START_LABEL }} {key: $START_KEY}), (n2:{{ END_LABEL }} {key: $END_KEY})
            MERGE (n1)-[r1:{{ TYPE }}]->(n2)-[r2:{{ REVERSE_TYPE }}]->(n1)
            {% if update_prop_body %}
            ON CREATE SET {{ prop_body }}
            ON MATCH SET {{ prop_body }}
            {% endif %}
            RETURN n1.key, n2.key
        """)

        prop_body_r1 = self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r1')
        prop_body_r2 = self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r2')
        prop_body = ' , '.join([prop_body_r1, prop_body_r2])

        return template.render(START_LABEL=rel_record["START_LABEL"],
                               END_LABEL=rel_record["END_LABEL"],
                               TYPE=rel_record["TYPE"],
                               REVERSE_TYPE=rel_record["REVERSE_TYPE"],
                               update_prop_body=prop_body_r1,
                               prop_body=prop_body)

    def _create_props_param(self, record_dict: dict) -> dict:
        params = {}
        for k, v in record_dict.items():
            if k.endswith(UNQUOTED_SUFFIX):
                k = k[:-len(UNQUOTED_SUFFIX)]

            params[k] = v
        return params

    def _create_props_body(self,
                           record_dict: dict,
                           excludes: Set,
                           identifier: str) -> str:
        """
        Creates properties body with params required for resolving template.

        e.g: Note that node.key3 is not quoted if header has UNQUOTED_SUFFIX.
        identifier.key1 = 'val1' , identifier.key2 = 'val2', identifier.key3 = val3

        :param record_dict: A dict represents CSV row
        :param excludes: set of excluded columns that does not need to be in properties
        (e.g: KEY, LABEL ...)
        :param identifier: identifier that will be used in CYPHER query as shown on above example
        :return: Properties body for Cypher statement
        """
        props = []
        for k, v in record_dict.items():
            if k in excludes:
                continue

            if k.endswith(UNQUOTED_SUFFIX):
                k = k[:-len(UNQUOTED_SUFFIX)]

            props.append(f'{identifier}.{k} = ${k}')

        if self.add_publisher_metadata:
            props.append(f"{identifier}.{PUBLISHED_TAG_PROPERTY_NAME} = '{self.publish_tag}'")
            props.append(f"{identifier}.{LAST_UPDATED_EPOCH_MS} = timestamp()")

        # add additional metatada fields from config
        for k, v in self.additional_fields.items():
            val = v if isinstance(v, int) or isinstance(v, float) else f"'{v}'"
            props.append(f"{identifier}.{k}= {val}")

        return ', '.join(props)

    def _execute_statement(self,
                           stmt: str,
                           tx: Transaction,
                           params: dict = None,
                           expect_result: bool = False) -> Transaction:
        """
        Executes statement against Neo4j. If execution fails, it rollsback and raise exception.
        If 'expect_result' flag is True, it confirms if result object is not null.
        :param stmt:
        :param tx:
        :param count:
        :param expect_result: By having this True, it will validate if result object is not None.
        :return:
        """
        try:
            LOGGER.debug('Executing statement: %s with params %s', stmt, params)

            result = tx.run(str(stmt), parameters=params)
            if expect_result and not result.single():
                raise RuntimeError(f'Failed to executed statement: {stmt}')

            self._count += 1
            if self._count > 1 and self._count % self._transaction_size == 0:
                tx.commit()
                LOGGER.info(f'Committed {self._count} statements so far')
                return self._session.begin_transaction()

            if self._count > 1 and self._count % self._progress_report_frequency == 0:
                LOGGER.info(f'Processed {self._count} statements so far')

            return tx
        except Exception as e:
            LOGGER.exception('Failed to execute Cypher query')
            if not tx.closed():
                tx.rollback()
            raise e

    def _try_create_index(self, label: str) -> None:
        """
        For any label seen first time for this publisher it will try to create unique index.
        Neo4j ignores a second creation in 3.x, but raises an error in 4.x.
        :param label:
        :return:
        """
        stmt = Template("""
            CREATE CONSTRAINT ON (node:{{ LABEL }}) ASSERT node.key IS UNIQUE
        """).render(LABEL=label)

        LOGGER.info(f'Trying to create index for label {label} if not exist: {stmt}')
        with self._driver.session(database=self._db_name) as session:
            try:
                session.run(stmt)
            except Neo4jError as e:
                if 'An equivalent constraint already exists' not in e.__str__():
                    raise
                # Else, swallow the exception, to make this function idempotent.
