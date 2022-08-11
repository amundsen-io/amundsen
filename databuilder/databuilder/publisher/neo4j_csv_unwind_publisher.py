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
from neo4j.exceptions import Neo4jError
from pyhocon import ConfigFactory, ConfigTree

from databuilder.publisher.base_publisher import Publisher

# Setting field_size_limit to solve the error below
# _csv.Error: field larger than field limit (131072)
# https://stackoverflow.com/a/54517228/5972935
csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

# Config keys
# A directory that contains CSV files for nodes
NODE_FILES_DIR = 'node_files_directory'
# A directory that contains CSV files for relationships
RELATION_FILES_DIR = 'relation_files_directory'
# A end point for Neo4j e.g: bolt://localhost:9999
NEO4J_END_POINT_KEY = 'neo4j_endpoint'
# A transaction size that determines how often it commits.
NEO4J_TRANSACTION_SIZE = 'neo4j_transaction_size'
# A boolean flag to make it fail if relationship is not created
NEO4J_RELATIONSHIP_CREATION_CONFIRM = 'neo4j_relationship_creation_confirm'

NEO4J_MAX_CONN_LIFE_TIME_SEC = 'neo4j_max_conn_life_time_sec'

# list of nodes that are create only, and not updated if match exists
NEO4J_CREATE_ONLY_NODES = 'neo4j_create_only_nodes'

NEO4J_USER = 'neo4j_user'
NEO4J_PASSWORD = 'neo4j_password'
# NEO4J_ENCRYPTED is a boolean indicating whether to use SSL/TLS when connecting
NEO4J_ENCRYPTED = 'neo4j_encrypted'
# NEO4J_VALIDATE_SSL is a boolean indicating whether to validate the server's SSL/TLS
# cert against system CAs
NEO4J_VALIDATE_SSL = 'neo4j_validate_ssl'

# This will be used to provide unique tag to the node and relationship
JOB_PUBLISH_TAG = 'job_publish_tag'

# any additional fields that should be added to nodes and rels through config
ADDITIONAL_FIELDS = 'additional_fields'

# Neo4j property name for published tag
PUBLISHED_TAG_PROPERTY_NAME = 'published_tag'

# Neo4j property name for last updated timestamp
LAST_UPDATED_EPOCH_MS = 'publisher_last_updated_epoch_ms'

# A boolean flag to indicate if publisher_metadata (e.g. published_tag,
# publisher_last_updated_epoch_ms)
# will be included as properties of the Neo4j nodes
ADD_PUBLISHER_METADATA = 'add_publisher_metadata'

# A boolean to indicate whether to publish reverse relationships, otherwise there will only be one direction
PUBLISH_REVERSE_RELATIONSHIPS = 'publish_reverse_relationships'

# If enabled, stops the publisher from updating a node or relationship
# created via the UI, e.g. a description or owner added manually by an Amundsen user.
# Such nodes/relationships will not have a 'published_tag' property that is set by databuilder.
PRESERVE_ADHOC_UI_DATA = 'preserve_adhoc_ui_data'

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
                                          NEO4J_RELATIONSHIP_CREATION_CONFIRM: False,
                                          NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
                                          NEO4J_ENCRYPTED: True,
                                          NEO4J_VALIDATE_SSL: False,
                                          ADDITIONAL_FIELDS: {},
                                          ADD_PUBLISHER_METADATA: True,
                                          PUBLISH_REVERSE_RELATIONSHIPS: True,
                                          PRESERVE_ADHOC_UI_DATA: False})

LOGGER = logging.getLogger(__name__)


class Neo4jCsvUnwindPublisher(Publisher):
    """
    A Publisher takes two folders for input and publishes to Neo4j.
    One folder will contain CSV file(s) for Node where the other folder will contain CSV
    file(s) for Relationship.

    Neo4j follows Label Node properties Graph and more information about this is in:
    https://neo4j.com/docs/developer-manual/current/introduction/graphdb-concepts/
    """

    def __init__(self) -> None:
        super(Neo4jCsvUnwindPublisher, self).__init__()

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(DEFAULT_CONFIG)

        self._count: int = 0
        self._node_files = self._list_files(conf, NODE_FILES_DIR)
        self._node_files_iter = iter(self._node_files)

        self._relation_files = self._list_files(conf, RELATION_FILES_DIR)
        self._relation_files_iter = iter(self._relation_files)

        trust = neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES if conf.get_bool(NEO4J_VALIDATE_SSL) \
            else neo4j.TRUST_ALL_CERTIFICATES
        neo4j_endpoint = conf.get_string(NEO4J_END_POINT_KEY)
        uri_scheme = neo4j_endpoint.split(':')[0]
        extra_configs = {}
        # Only unsecured URI schemes accept 'encrypted' and 'trust' configs
        if uri_scheme in ['bolt', 'neo4j']:
            extra_configs = {'encrypted': conf.get_bool(NEO4J_ENCRYPTED), 'trust': trust}
        self._driver = \
            GraphDatabase.driver(uri=neo4j_endpoint,
                                 max_connection_lifetime=conf.get_int(NEO4J_MAX_CONN_LIFE_TIME_SEC),
                                 auth=(conf.get_string(NEO4J_USER), conf.get_string(NEO4J_PASSWORD)),
                                 **extra_configs)

        self._transaction_size = conf.get_int(NEO4J_TRANSACTION_SIZE)
        self._confirm_rel_created = conf.get_bool(NEO4J_RELATIONSHIP_CREATION_CONFIRM)

        # config is list of node label.
        # When set, this list specifies a list of nodes that shouldn't be updated, if exists
        self.create_only_nodes = set(conf.get_list(NEO4J_CREATE_ONLY_NODES, default=[]))
        self.labels: Set[str] = set()
        self.publish_tag: str = conf.get_string(JOB_PUBLISH_TAG)
        self.additional_fields: Dict = conf.get(ADDITIONAL_FIELDS)
        self.add_publisher_metadata: bool = conf.get_bool(ADD_PUBLISHER_METADATA)
        self.publish_reverse_relationships: bool = conf.get_bool(PUBLISH_REVERSE_RELATIONSHIPS)
        self._preserve_adhoc_ui_data = conf.get_bool(PRESERVE_ADHOC_UI_DATA)
        if self.add_publisher_metadata and not self.publish_tag:
            raise Exception(f'{JOB_PUBLISH_TAG} should not be empty')

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
        while True:
            try:
                node_file = next(self._node_files_iter)
                self._publish_node(node_file)
            except StopIteration:
                break

        LOGGER.info('Publishing Relationship files: %s', self._relation_files)
        while True:
            try:
                relation_file = next(self._relation_files_iter)
                self._publish_relation(relation_file)
            except StopIteration:
                break

        LOGGER.info('Committed total %i statements', self._count)

        # TODO: Add statsd support
        LOGGER.info('Successfully published. Elapsed: %i seconds', time.time() - start)

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

    def _write_transactions(self,
                            records: List[dict],
                            stmt: str,
                            confirm_rel_created: bool = False):
        params_list = []
        start_idx = 0
        while start_idx < len(records):
            stop_idx = min(start_idx + self._transaction_size, len(records))

            for i in range(start_idx, stop_idx):
                params_list.append(self._create_props_param(records[i]))

            with self._driver.session() as session:
                session.write_transaction(self._execute_statement, stmt, {'batch': params_list},
                                          expect_result=confirm_rel_created)

            params_list.clear()
            start_idx = start_idx + self._transaction_size

    def _publish_node(self, node_file: str):
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
            all_node_records = pandas.read_csv(node_csv, na_filter=False).to_dict(orient="records")
            if len(all_node_records) > 0:
                stmt = self.create_node_merge_statement(node_record=all_node_records[0])

            self._write_transactions(all_node_records, stmt)

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
            UNWIND $batch AS row
            MERGE (node:{{ LABEL }} {key: row.KEY})
            ON CREATE SET {{ PROP_BODY_CREATE }}
            {% if update %} ON MATCH SET {{ PROP_BODY_UPDATE }} {% endif %}
        """)

        prop_body_create = self._create_props_body(node_record, NODE_REQUIRED_KEYS, 'node')

        prop_body_update = prop_body_create
        if self._preserve_adhoc_ui_data:
            prop_body_update = self._create_props_body(node_record, NODE_REQUIRED_KEYS, 'node', True)

        return template.render(LABEL=node_record["LABEL"],
                               PROP_BODY_CREATE=prop_body_create,
                               PROP_BODY_UPDATE=prop_body_update,
                               update=(not self.is_create_only_node(node_record)))

    def _publish_relation(self, relation_file: str):
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

        with open(relation_file, 'r', encoding='utf8') as relation_csv:
            all_rel_records = pandas.read_csv(relation_csv, na_filter=False).to_dict(orient="records")
            if len(all_rel_records) > 0:
                stmt = self.create_relationship_merge_statement(rel_record=all_rel_records[0])

            self._write_transactions(all_rel_records, stmt, self._confirm_rel_created)

    def create_relationship_merge_statement(self, rel_record: dict) -> str:
        """
        Creates relationship merge statement
        :param rel_record:
        :return:
        """
        template = Template("""
            UNWIND $batch as row
            MATCH (n1:{{ START_LABEL }} {key: row.START_KEY}), (n2:{{ END_LABEL }} {key: row.END_KEY})
            MERGE {{ relationship_stmt }}
            {% if update_prop_body %}
            ON CREATE SET {{ prop_body_create }}
            ON MATCH SET {{ prop_body_update }}
            {% endif %}
            RETURN n1.key, n2.key
        """)

        two_way_relationship = Template("""
            (n1)-[r1:{{ TYPE }}]->(n2)-[r2:{{ REVERSE_TYPE }}]->(n1)
        """).render(TYPE=rel_record["TYPE"], REVERSE_TYPE=rel_record["REVERSE_TYPE"])
        one_way_relationship = Template("""
            (n1)-[r1:{{ TYPE }}]->(n2)
        """).render(TYPE=rel_record["TYPE"])

        prop_body_r1 = self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r1')
        prop_body_r2 = self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r2')
        prop_body_create = ' , '.join([prop_body_r1, prop_body_r2])\
            if self.publish_reverse_relationships else prop_body_r1

        prop_body_update = prop_body_create
        if self._preserve_adhoc_ui_data:
            prop_body_r1 = self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r1', True)
            prop_body_r2 = self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r2', True)
            prop_body_update = ' , '.join([prop_body_r1, prop_body_r2]) \
                if self.publish_reverse_relationships else prop_body_r1

        return template.render(START_LABEL=rel_record["START_LABEL"],
                               END_LABEL=rel_record["END_LABEL"],
                               relationship_stmt=two_way_relationship if self.publish_reverse_relationships
                               else one_way_relationship,
                               update_prop_body=prop_body_r1,
                               prop_body_create=prop_body_create,
                               prop_body_update=prop_body_update)

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
                           identifier: str,
                           rename_id_to_preserve_ui_data: bool = False) -> str:
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
        # For SET, if the evaluated expression is null, no action is performed. I.e. `SET (null).foo = 5` is a noop.
        # See https://neo4j.com/docs/cypher-manual/current/clauses/set/
        if rename_id_to_preserve_ui_data:
            identifier = \
                f"(CASE WHEN {identifier}.{PUBLISHED_TAG_PROPERTY_NAME} IS NOT NULL THEN {identifier} ELSE null END)"

        props = []
        for k, v in record_dict.items():
            if k in excludes:
                continue

            if k.endswith(UNQUOTED_SUFFIX):
                k = k[:-len(UNQUOTED_SUFFIX)]

            props.append(f'{identifier}.{k} = row.{k}')

        if self.add_publisher_metadata:
            props.append(f"{identifier}.{PUBLISHED_TAG_PROPERTY_NAME} = '{self.publish_tag}'")
            props.append(f"{identifier}.{LAST_UPDATED_EPOCH_MS} = timestamp()")

        # add additional metadata fields from config
        for k, v in self.additional_fields.items():
            val = v if isinstance(v, int) or isinstance(v, float) else f"'{v}'"
            props.append(f"{identifier}.{k}= {val}")

        return ', '.join(props)

    def _execute_statement(self,
                           tx: Transaction,
                           stmt: str,
                           params: dict = None,
                           expect_result: bool = False):
        """
        Executes statement against Neo4j. If execution fails, it rollsback and raise exception.
        If 'expect_result' flag is True, it confirms if result object is not null.
        :param tx:
        :param stmt:
        :param expect_result: By having this True, it will validate if result object is not None.
        :return:
        """

        LOGGER.debug('Executing statement: %s with params %s', stmt, params)

        result = tx.run(stmt, parameters=params)
        if expect_result and not result.single():
            raise RuntimeError(f'Failed to executed statement: {stmt}')

        self._count += len(params['batch'])
        LOGGER.info(f'Committed {self._count} rows so far')

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
        with self._driver.session() as session:
            try:
                session.run(stmt)
            except Neo4jError as e:
                if 'An equivalent constraint already exists' not in e.__str__():
                    raise
                # Else, swallow the exception, to make this function idempotent.
