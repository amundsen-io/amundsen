import copy
import csv
import logging
import time
from os import listdir
from os.path import isfile, join
from string import Template

import six
from neo4j.v1 import GraphDatabase, Transaction  # noqa: F401
from pyhocon import ConfigFactory  # noqa: F401
from pyhocon import ConfigTree  # noqa: F401
from typing import Set, List  # noqa: F401

from databuilder.publisher.base_publisher import Publisher

# Config keys
# A directory that contains CSV files for nodes
NODE_FILES_DIR = 'node_files_directory'
# A directory that contains CSV files for relationships
RELATION_FILES_DIR = 'relation_files_directory'
# A end point for Neo4j e.g: bolt://localhost:9999
NEO4J_END_POINT_KEY = 'neo4j_endpoint'
# A transaction size that determines how often it commits.
NEO4J_TRANSCATION_SIZE = 'neo4j_transaction_size'
# A boolean flag to make it fail if relationship is not created
NEO4J_RELATIONSHIP_CREATION_CONFIRM = 'neo4j_relationship_creation_confirm'

NEO4J_MAX_CONN_LIFE_TIME_SEC = 'neo4j_max_conn_life_time_sec'

# list of nodes that are create only, and not updated if match exists
NEO4J_CREATE_ONLY_NODES = 'neo4j_create_only_nodes'

NEO4J_USER = 'neo4j_user'
NEO4J_PASSWORD = 'neo4j_password'

# This will be used to provide unique tag to the node and relationship
JOB_PUBLISH_TAG = 'job_publish_tag'

# Neo4j property name for published tag
PUBLISHED_TAG_PROPERTY_NAME = 'published_tag'

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
                                          NEO4J_RELATIONSHIP_CREATION_CONFIRM: False,
                                          NEO4J_MAX_CONN_LIFE_TIME_SEC: 50})

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
        pass

    def init(self, conf):
        # type: (ConfigTree) -> None
        conf = conf.with_fallback(DEFAULT_CONFIG)

        self._node_files = self._list_files(conf, NODE_FILES_DIR)
        self._node_files_iter = iter(self._node_files)

        self._relation_files = self._list_files(conf, RELATION_FILES_DIR)
        self._relation_files_iter = iter(self._relation_files)

        self._driver = \
            GraphDatabase.driver(conf.get_string(NEO4J_END_POINT_KEY),
                                 max_connection_life_time=50,
                                 auth=(conf.get_string(NEO4J_USER), conf.get_string(NEO4J_PASSWORD)))
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

    def publish(self):
        # type: () -> None
        """
        Publishes Nodes first and then Relations
        :return:
        """

        start = time.time()

        LOGGER.info('Publishing Node files: {}'.format(self._node_files))
        while True:
            try:
                node_file = next(self._node_files_iter)
                self._publish_node(node_file)
            except StopIteration:
                break

        LOGGER.info('Publishing Relationship files: {}'.format(self._relation_files))
        while True:
            try:
                relation_file = next(self._relation_files_iter)
                self._publish_relation(relation_file)
            except StopIteration:
                break

        # TODO: Add statsd support
        LOGGER.info('Successfully published. Elapsed: {} seconds'.format(time.time() - start))

    def get_scope(self):
        # type: () -> str
        return 'publisher.neo4j'

    def _publish_node(self, node_file):
        # type: (str) -> None
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
        tx = self._session.begin_transaction()
        with open(node_file, 'r') as node_csv:
            for count, node_record in enumerate(csv.DictReader(node_csv)):
                label = node_record[NODE_LABEL_KEY]
                # If label is seen for the first time, try creating unique index
                if label not in self.labels:
                    tx.commit()  # Transaction needs to be committed as index update will make transaction to abort.
                    tx.close()
                    LOGGER.info('Committed {} records'.format(count + 1))

                    self._try_create_index(label)
                    self.labels.add(label)
                    tx = self._session.begin_transaction()

                stmt = self.create_node_merge_statement(node_record=node_record)
                tx = self._execute_statement(stmt, tx, count)

        tx.commit()
        tx.close()
        LOGGER.info('Committed {} records'.format(count + 1))

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

    def _publish_relation(self, relation_file):
        # type: (str) -> None
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

        tx = self._session.begin_transaction()
        with open(relation_file, 'r') as relation_csv:
            for count, rel_record in enumerate(csv.DictReader(relation_csv)):
                stmt = self.create_relationship_merge_statement(rel_record=rel_record)
                tx = self._execute_statement(stmt, tx, count,
                                             expect_result=self._confirm_rel_created)

        tx.commit()
        tx.close()
        LOGGER.info('Committed {} records'.format(count + 1))

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

            # escape quote for Cypher query
            # if isinstance(str, v):
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

        return ', '.join(props)

    def _execute_statement(self,
                           stmt,
                           tx,
                           count,
                           expect_result=False):
        # type: (str, Transaction, int, bool) -> Transaction

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
                LOGGER.debug('Executing statement: {}'.format(stmt))

            if six.PY2:
                result = tx.run(unicode(stmt, errors='ignore')) # noqa
            else:
                result = tx.run(str(stmt).encode('utf-8', 'ignore'))
            if expect_result and not result.single():
                raise RuntimeError('Failed to executed statement: {}'.format(stmt))

            if count > 1 and count % self._transaction_size == 0:
                tx.commit()
                tx.close()
                LOGGER.info('Committed {} records so far'.format(count))
                return self._session.begin_transaction()

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
        There's no side effect on Neo4j side issuing index creation for existing index.
        :param label:
        :return:
        """
        stmt = CREATE_UNIQUE_INDEX_TEMPLATE.substitute(LABEL=label)
        LOGGER.info('Trying to create index for label {label} if not exist: {stmt}'.format(label=label,
                                                                                           stmt=stmt))
        with self._driver.session() as session:
            session.run(stmt)
