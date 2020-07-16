# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import copy
import csv
import ctypes
from io import open
import logging
import time
from os import listdir
from os.path import isfile, join
from string import Template

import six
from neo4j import GraphDatabase, Transaction  # noqa: F401
import neo4j
from neo4j.exceptions import CypherError
from pyhocon import ConfigFactory  # noqa: F401
from pyhocon import ConfigTree  # noqa: F401
from typing import Set, List  # noqa: F401

from databuilder.publisher.base_publisher import Publisher
from databuilder.publisher.neo4j_preprocessor import NoopRelationPreprocessor


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
NEO4J_TRANSCATION_SIZE = 'neo4j_transaction_size'
# A progress report frequency that determines how often it report the progress.
NEO4J_PROGRESS_REPORT_FREQUENCY = 'neo4j_progress_report_frequency'
# A boolean flag to make it fail if relationship is not created
NEO4J_RELATIONSHIP_CREATION_CONFIRM = 'neo4j_relationship_creation_confirm'

NEO4J_MAX_CONN_LIFE_TIME_SEC = 'neo4j_max_conn_life_time_sec'

# list of nodes that are create only, and not updated if match exists
NEO4J_CREATE_ONLY_NODES = 'neo4j_create_only_nodes'

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

DEFAULT_CONFIG = ConfigFactory.from_dict({NEO4J_TRANSCATION_SIZE: 500,
                                          NEO4J_PROGRESS_REPORT_FREQUENCY: 500,
                                          NEO4J_RELATIONSHIP_CREATION_CONFIRM: False,
                                          NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
                                          NEO4J_ENCRYPTED: True,
                                          NEO4J_VALIDATE_SSL: False,
                                          RELATION_PREPROCESSOR: NoopRelationPreprocessor()})

NODE_MERGE_TEMPLATE = Template("""MERGE (node:$LABEL {key: '${KEY}'})
ON CREATE SET ${create_prop_body}
${update_statement}""")

NODE_UPDATE_TEMPLATE = Template("""ON MATCH SET ${update_prop_body}""")

RELATION_MERGE_TEMPLATE = Template("""MATCH (n1:$START_LABEL {key: '${START_KEY}'}),
(n2:$END_LABEL {key: '${END_KEY}'})
MERGE (n1)-[r1:$TYPE]->(n2)-[r2:$REVERSE_TYPE]->(n1)
$PROP_STMT RETURN n1.key, n2.key""")

CREATE_UNIQUE_INDEX_TEMPLATE = Template('CREATE CONSTRAINT ON (node:${LABEL}) ASSERT node.key IS UNIQUE')

LOGGER = logging.getLogger(__name__)


class Neo4jCsvPublisher(Publisher):
    """
    A Publisher takes two folders for input and publishes to Neo4j.
    One folder will contain CSV file(s) for Node where the other folder will contain CSV file(s) for Relationship.

    Neo4j follows Label Node properties Graph and more information about this is in:
    https://neo4j.com/docs/developer-manual/current/introduction/graphdb-concepts/

    #TODO User UNWIND batch operation for better performance
    """

    def __init__(self):
        # type: () -> None
        super(Neo4jCsvPublisher, self).__init__()

    def init(self, conf):
        # type: (ConfigTree) -> None
        conf = conf.with_fallback(DEFAULT_CONFIG)

        self._count = 0  # type: int
        self._progress_report_frequency = conf.get_int(NEO4J_PROGRESS_REPORT_FREQUENCY)
        self._node_files = self._list_files(conf, NODE_FILES_DIR)
        self._node_files_iter = iter(self._node_files)

        self._relation_files = self._list_files(conf, RELATION_FILES_DIR)
        self._relation_files_iter = iter(self._relation_files)

        trust = neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES if conf.get_bool(NEO4J_VALIDATE_SSL) \
            else neo4j.TRUST_ALL_CERTIFICATES
        self._driver = \
            GraphDatabase.driver(conf.get_string(NEO4J_END_POINT_KEY),
                                 max_connection_life_time=conf.get_int(NEO4J_MAX_CONN_LIFE_TIME_SEC),
                                 auth=(conf.get_string(NEO4J_USER), conf.get_string(NEO4J_PASSWORD)),
                                 encrypted=conf.get_bool(NEO4J_ENCRYPTED),
                                 trust=trust)
        self._transaction_size = conf.get_int(NEO4J_TRANSCATION_SIZE)
        self._session = self._driver.session()
        self._confirm_rel_created = conf.get_bool(NEO4J_RELATIONSHIP_CREATION_CONFIRM)

        # config is list of node label.
        # When set, this list specifies a list of nodes that shouldn't be updated, if exists
        self.create_only_nodes = set(conf.get_list(NEO4J_CREATE_ONLY_NODES, default=[]))
        self.labels = set()  # type: Set[str]
        self.publish_tag = conf.get_string(JOB_PUBLISH_TAG)  # type: str
        if not self.publish_tag:
            raise Exception('{} should not be empty'.format(JOB_PUBLISH_TAG))

        self._relation_preprocessor = conf.get(RELATION_PREPROCESSOR)

        LOGGER.info('Publishing Node csv files {}, and Relation CSV files {}'
                    .format(self._node_files, self._relation_files))

    def _list_files(self, conf, path_key):
        # type: (ConfigTree, str) -> List[str]
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

    def publish_impl(self):  # noqa: C901
        # type: () -> None
        """
        Publishes Nodes first and then Relations
        :return:
        """

        start = time.time()

        LOGGER.info('Creating indices using Node files: {}'.format(self._node_files))
        for node_file in self._node_files:
            self._create_indices(node_file=node_file)

        LOGGER.info('Publishing Node files: {}'.format(self._node_files))
        try:
            tx = self._session.begin_transaction()
            while True:
                try:
                    node_file = next(self._node_files_iter)
                    tx = self._publish_node(node_file, tx=tx)
                except StopIteration:
                    break

            LOGGER.info('Publishing Relationship files: {}'.format(self._relation_files))
            while True:
                try:
                    relation_file = next(self._relation_files_iter)
                    tx = self._publish_relation(relation_file, tx=tx)
                except StopIteration:
                    break

            tx.commit()
            LOGGER.info('Committed total {} statements'.format(self._count))

            # TODO: Add statsd support
            LOGGER.info('Successfully published. Elapsed: {} seconds'.format(time.time() - start))
        except Exception as e:
            LOGGER.exception('Failed to publish. Rolling back.')
            if not tx.closed():
                tx.rollback()
            raise e

    def get_scope(self):
        # type: () -> str
        return 'publisher.neo4j'

    def _create_indices(self, node_file):
        """
        Go over the node file and try creating unique index
        :param node_file:
        :return:
        """
        # type: (str) -> None
        LOGGER.info('Creating indices. (Existing indices will be ignored)')

        with open(node_file, 'r', encoding='utf8') as node_csv:
            for node_record in csv.DictReader(node_csv):
                label = node_record[NODE_LABEL_KEY]
                if label not in self.labels:
                    self._try_create_index(label)
                    self.labels.add(label)

        LOGGER.info('Indices have been created.')

    def _publish_node(self, node_file, tx):
        # type: (str, Transaction) -> Transaction
        """
        Iterate over the csv records of a file, each csv record transform to Merge statement and will be executed.
        All nodes should have a unique key, and this method will try to create unique index on the LABEL when it sees
        first time within a job scope.
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
            for count, node_record in enumerate(csv.DictReader(node_csv)):
                stmt = self.create_node_merge_statement(node_record=node_record)
                tx = self._execute_statement(stmt, tx)
        return tx

    def is_create_only_node(self, node_record):
        # type: (dict) -> bool
        """
        Check if node can be updated
        :param node_record:
        :return:
        """
        if self.create_only_nodes:
            return node_record[NODE_LABEL_KEY] in self.create_only_nodes
        else:
            return False

    def create_node_merge_statement(self, node_record):
        # type: (dict) -> str
        """
        Creates node merge statement
        :param node_record:
        :return:
        """
        params = copy.deepcopy(node_record)
        params['create_prop_body'] = self._create_props_body(node_record, NODE_REQUIRED_KEYS, 'node')

        update_statement = ''
        if not self.is_create_only_node(node_record):
            update_prop_body = self._create_props_body(node_record, NODE_REQUIRED_KEYS, 'node')
            update_statement = NODE_UPDATE_TEMPLATE.substitute(update_prop_body=update_prop_body)
        params['update_statement'] = update_statement

        return NODE_MERGE_TEMPLATE.substitute(params)

    def _publish_relation(self, relation_file, tx):
        # type: (str, Transaction) -> Transaction
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
            LOGGER.info('Pre-processing relation with {}'.format(self._relation_preprocessor))

            count = 0
            with open(relation_file, 'r', encoding='utf8') as relation_csv:
                for rel_record in csv.DictReader(relation_csv):
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

            LOGGER.info('Executed pre-processing Cypher statement {} times'.format(count))

        with open(relation_file, 'r', encoding='utf8') as relation_csv:
            for count, rel_record in enumerate(csv.DictReader(relation_csv)):
                stmt = self.create_relationship_merge_statement(rel_record=rel_record)
                tx = self._execute_statement(stmt, tx,
                                             expect_result=self._confirm_rel_created)

        return tx

    def create_relationship_merge_statement(self, rel_record):
        # type: (dict) -> str
        """
        Creates relationship merge statement
        :param rel_record:
        :return:
        """
        param = copy.deepcopy(rel_record)
        create_prop_body = self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r1')
        param['PROP_STMT'] = ' '  # No properties for relationship by default

        if create_prop_body:
            # We need one more body for reverse relation
            create_prop_body = ' , '.join([create_prop_body,
                                           self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r2')])
            update_prop_body = ' , '.join([self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r1'),
                                           self._create_props_body(rel_record, RELATION_REQUIRED_KEYS, 'r2')])

            param['PROP_STMT'] = """ON CREATE SET {create_prop_body}
ON MATCH SET {update_prop_body}""".format(create_prop_body=create_prop_body,
                                          update_prop_body=update_prop_body)

        return RELATION_MERGE_TEMPLATE.substitute(param)

    def _create_props_body(self,
                           record_dict,
                           excludes,
                           identifier):
        # type: (dict, Set, str) -> str
        """
        Creates properties body with params required for resolving template.

        e.g: Note that node.key3 is not quoted if header has UNQUOTED_SUFFIX.
        identifier.key1 = 'val1' , identifier.key2 = 'val2', identifier.key3 = val3

        :param record_dict: A dict represents CSV row
        :param excludes: set of excluded columns that does not need to be in properties (e.g: KEY, LABEL ...)
        :param identifier: identifier that will be used in CYPHER query as shown on above example
        :param is_update: Creates property body for update statement in MERGE
        :return: Properties body for Cypher statement
        """
        template_params = {}
        props = []
        for k, v in six.iteritems(record_dict):
            if k in excludes:
                template_params[k] = v
                continue

            # if isinstance(str, v):
            # escape backslash for Cypher query
            v = v.replace('\\', '\\\\')
            # escape quote for Cypher query
            v = v.replace('\'', "\\'")

            if k.endswith(UNQUOTED_SUFFIX):
                k = k[:-len(UNQUOTED_SUFFIX)]
                props.append('{id}.{key} = {val}'.format(id=identifier, key=k, val=v))
            else:
                props.append("""{id}.{key} = '{val}'""".format(id=identifier, key=k, val=v))

            template_params[k] = v

        props.append("""{id}.{key} = '{val}'""".format(id=identifier,
                                                       key=PUBLISHED_TAG_PROPERTY_NAME,
                                                       val=self.publish_tag))

        props.append("""{id}.{key} = {val}""".format(id=identifier,
                                                     key=LAST_UPDATED_EPOCH_MS,
                                                     val='timestamp()'))

        return ', '.join(props)

    def _execute_statement(self,
                           stmt,
                           tx,
                           params=None,
                           expect_result=False):
        # type: (str, Transaction, bool) -> Transaction
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
            if LOGGER.isEnabledFor(logging.DEBUG):
                LOGGER.debug('Executing statement: {} with params {}'.format(stmt, params))

            if six.PY2:
                result = tx.run(unicode(stmt, errors='ignore'), parameters=params)  # noqa
            else:
                result = tx.run(str(stmt).encode('utf-8', 'ignore'), parameters=params)
            if expect_result and not result.single():
                raise RuntimeError('Failed to executed statement: {}'.format(stmt))

            self._count += 1
            if self._count > 1 and self._count % self._transaction_size == 0:
                tx.commit()
                LOGGER.info('Committed {} statements so far'.format(self._count))
                return self._session.begin_transaction()

            if self._count > 1 and self._count % self._progress_report_frequency == 0:
                LOGGER.info('Processed {} statements so far'.format(self._count))

            return tx
        except Exception as e:
            LOGGER.exception('Failed to execute Cypher query')
            if not tx.closed():
                tx.rollback()
            raise e

    def _try_create_index(self,
                          label):
        # type: (str) -> None
        """
        For any label seen first time for this publisher it will try to create unique index.
        Neo4j ignores a second creation in 3.x, but raises an error in 4.x.
        :param label:
        :return:
        """
        stmt = CREATE_UNIQUE_INDEX_TEMPLATE.substitute(LABEL=label)
        LOGGER.info('Trying to create index for label {label} if not exist: {stmt}'.format(label=label,
                                                                                           stmt=stmt))
        with self._driver.session() as session:
            try:
                session.run(stmt)
            except CypherError as e:
                if 'An equivalent constraint already exists' not in e.__str__():
                    raise
                # Else, swallow the exception, to make this function idempotent.
