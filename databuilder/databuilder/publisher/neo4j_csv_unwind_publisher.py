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
from neo4j import (
    GraphDatabase, Neo4jDriver, Transaction,
)
from neo4j.api import (
    SECURITY_TYPE_SECURE, SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, parse_neo4j_uri,
)
from neo4j.exceptions import Neo4jError
from pyhocon import ConfigFactory, ConfigTree

from databuilder.models.graph_serializable import (
    NODE_KEY, NODE_LABEL, RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY,
    RELATION_START_LABEL, RELATION_TYPE,
)
from databuilder.publisher.base_publisher import Publisher
from databuilder.publisher.publisher_config_constants import (
    Neo4jCsvPublisherConfigs, PublishBehaviorConfigs, PublisherConfigs,
)

# Setting field_size_limit to solve the error below
# _csv.Error: field larger than field limit (131072)
# https://stackoverflow.com/a/54517228/5972935
csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

# Required columns for Node
NODE_REQUIRED_KEYS = {NODE_LABEL, NODE_KEY}
# Required columns for Relationship
RELATION_REQUIRED_KEYS = {RELATION_START_LABEL, RELATION_START_KEY,
                          RELATION_END_LABEL, RELATION_END_KEY,
                          RELATION_TYPE, RELATION_REVERSE_TYPE}

DEFAULT_CONFIG = ConfigFactory.from_dict({Neo4jCsvPublisherConfigs.NEO4J_TRANSACTION_SIZE: 500,
                                          Neo4jCsvPublisherConfigs.NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
                                          Neo4jCsvPublisherConfigs.NEO4J_DATABASE_NAME: neo4j.DEFAULT_DATABASE,
                                          PublisherConfigs.ADDITIONAL_PUBLISHER_METADATA_FIELDS: {},
                                          PublishBehaviorConfigs.ADD_PUBLISHER_METADATA: True,
                                          PublishBehaviorConfigs.PUBLISH_REVERSE_RELATIONSHIPS: True,
                                          PublishBehaviorConfigs.PRESERVE_ADHOC_UI_DATA: False})

LOGGER = logging.getLogger(__name__)


class Neo4jCsvUnwindPublisher(Publisher):
    """
    A Publisher takes two folders for input and publishes to Neo4j.
    One folder will contain CSV file(s) for Node where the other folder will contain CSV
    file(s) for Relationship.

    Neo4j follows Label Node properties Graph and more information about this is in:
    https://neo4j.com/docs/developer-manual/current/introduction/graphdb-concepts/
    """

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(DEFAULT_CONFIG)

        self._count: int = 0
        self._node_files = self._list_files(conf, PublisherConfigs.NODE_FILES_DIR)
        self._node_files_iter = iter(self._node_files)

        self._relation_files = self._list_files(conf, PublisherConfigs.RELATION_FILES_DIR)
        self._relation_files_iter = iter(self._relation_files)

        self._driver = self._driver_init(conf)
        self._db_name = conf.get_string(Neo4jCsvPublisherConfigs.NEO4J_DATABASE_NAME)
        self._transaction_size = conf.get_int(Neo4jCsvPublisherConfigs.NEO4J_TRANSACTION_SIZE)

        # config is list of node label.
        # When set, this list specifies a list of nodes that shouldn't be updated, if exists
        self._create_only_nodes = set(conf.get_list(Neo4jCsvPublisherConfigs.NEO4J_CREATE_ONLY_NODES, default=[]))
        self._labels: Set[str] = set()
        self._publish_tag: str = conf.get_string(PublisherConfigs.JOB_PUBLISH_TAG)
        self._additional_publisher_metadata_fields: Dict =\
            conf.get(PublisherConfigs.ADDITIONAL_PUBLISHER_METADATA_FIELDS)
        self._add_publisher_metadata: bool = conf.get_bool(PublishBehaviorConfigs.ADD_PUBLISHER_METADATA)
        self._publish_reverse_relationships: bool = conf.get_bool(PublishBehaviorConfigs.PUBLISH_REVERSE_RELATIONSHIPS)
        self._preserve_adhoc_ui_data = conf.get_bool(PublishBehaviorConfigs.PRESERVE_ADHOC_UI_DATA)
        if self._add_publisher_metadata and not self._publish_tag:
            raise Exception(f'{PublisherConfigs.JOB_PUBLISH_TAG} should not be empty')

        LOGGER.info('Publishing Node csv files %s, and Relation CSV files %s',
                    self._node_files,
                    self._relation_files)

    def _driver_init(self, conf: ConfigTree) -> Neo4jDriver:
        uri = conf.get_string(Neo4jCsvPublisherConfigs.NEO4J_END_POINT_KEY)
        driver_args = {
            'uri': uri,
            'max_connection_lifetime': conf.get_int(Neo4jCsvPublisherConfigs.NEO4J_MAX_CONN_LIFE_TIME_SEC),
            'auth': (conf.get_string(Neo4jCsvPublisherConfigs.NEO4J_USER),
                     conf.get_string(Neo4jCsvPublisherConfigs.NEO4J_PASSWORD)),
        }

        # if URI scheme not secure set `trust`` and `encrypted` to default values
        # https://neo4j.com/docs/api/python-driver/current/api.html#uri
        _, security_type, _ = parse_neo4j_uri(uri=uri)
        if security_type not in [SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, SECURITY_TYPE_SECURE]:
            default_security_conf = {'trust': neo4j.TRUST_ALL_CERTIFICATES, 'encrypted': True}
            driver_args.update(default_security_conf)

        # if NEO4J_VALIDATE_SSL or NEO4J_ENCRYPTED are set in config pass them to the driver
        validate_ssl_conf = conf.get(Neo4jCsvPublisherConfigs.NEO4J_VALIDATE_SSL, None)
        encrypted_conf = conf.get(Neo4jCsvPublisherConfigs.NEO4J_ENCRYPTED, None)
        if validate_ssl_conf is not None:
            driver_args['trust'] = neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES if validate_ssl_conf \
                else neo4j.TRUST_ALL_CERTIFICATES
        if encrypted_conf is not None:
            driver_args['encrypted'] = encrypted_conf

        return GraphDatabase.driver(**driver_args)

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
                label = node_record[NODE_LABEL]
                if label not in self._labels:
                    with self._driver.session(database=self._db_name) as session:
                        try:
                            session.write_transaction(self._try_create_index, label)
                        except Neo4jError as e:
                            if 'An equivalent constraint already exists' not in e.__str__():
                                raise
                            # Else, swallow the exception, to make this function idempotent.
                    self._labels.add(label)

        LOGGER.info('Indices have been created.')

    def _write_transactions(self,
                            records: List[dict],
                            stmt: str) -> None:
        params_list = []
        start_idx = 0
        while start_idx < len(records):
            stop_idx = min(start_idx + self._transaction_size, len(records))

            for i in range(start_idx, stop_idx):
                params_list.append(self._create_props_param(records[i]))

            with self._driver.session(database=self._db_name) as session:
                session.write_transaction(self._execute_statement, stmt, {'batch': params_list})

            params_list.clear()
            start_idx = start_idx + self._transaction_size

    def _publish_node(self, node_file: str) -> None:
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

        prop_body_create = self._create_props_body(self._get_props_body_keys(node_record, NODE_REQUIRED_KEYS), 'node')

        prop_body_update = prop_body_create
        if self._preserve_adhoc_ui_data:
            prop_body_update = self._create_props_body(self._get_props_body_keys(node_record, NODE_REQUIRED_KEYS),
                                                       'node', True)

        return template.render(LABEL=node_record[NODE_LABEL],
                               PROP_BODY_CREATE=prop_body_create,
                               PROP_BODY_UPDATE=prop_body_update,
                               update=(not node_record[NODE_LABEL] in self._create_only_nodes))

    def _publish_relation(self, relation_file: str) -> None:
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

            self._write_transactions(all_rel_records, stmt)

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
        """).render(TYPE=rel_record[RELATION_TYPE], REVERSE_TYPE=rel_record[RELATION_REVERSE_TYPE])
        one_way_relationship = Template("""
            (n1)-[r1:{{ TYPE }}]->(n2)
        """).render(TYPE=rel_record[RELATION_TYPE])

        prop_body_template = Template("""{{ prop_body_r1 }} , {{ prop_body_r2 }}""")

        prop_body_r1 = self._create_props_body(self._get_props_body_keys(rel_record, RELATION_REQUIRED_KEYS), 'r1')
        prop_body_r2 = self._create_props_body(self._get_props_body_keys(rel_record, RELATION_REQUIRED_KEYS), 'r2')
        prop_body_create = prop_body_template.render(prop_body_r1=prop_body_r1, prop_body_r2=prop_body_r2)\
            if self._publish_reverse_relationships else prop_body_r1

        prop_body_update = prop_body_create
        if self._preserve_adhoc_ui_data:
            prop_body_r1 = self._create_props_body(self._get_props_body_keys(rel_record, RELATION_REQUIRED_KEYS),
                                                   'r1', True)
            prop_body_r2 = self._create_props_body(self._get_props_body_keys(rel_record, RELATION_REQUIRED_KEYS),
                                                   'r2', True)
            prop_body_update = prop_body_template.render(prop_body_r1=prop_body_r1, prop_body_r2=prop_body_r2)\
                if self._publish_reverse_relationships else prop_body_r1

        return template.render(START_LABEL=rel_record[RELATION_START_LABEL],
                               END_LABEL=rel_record[RELATION_END_LABEL],
                               relationship_stmt=two_way_relationship if self._publish_reverse_relationships
                               else one_way_relationship,
                               update_prop_body=prop_body_r1,
                               prop_body_create=prop_body_create,
                               prop_body_update=prop_body_update)

    def _create_props_param(self, record_dict: dict) -> dict:
        """
        Create a dict of all the params for a given record
        :param record_dict:
        """
        params = {}

        for k, v in {**record_dict, **dict(self._additional_publisher_metadata_fields)}.items():
            params[self._strip_unquoted_suffix(k)] = v

        return params

    def _strip_unquoted_suffix(self, key: str) -> str:
        return key[:-len(PublisherConfigs.UNQUOTED_SUFFIX)] if key.endswith(PublisherConfigs.UNQUOTED_SUFFIX) else key

    def _get_props_body_keys(self, record: dict, exclude_keys: Set) -> Set:
        """
        Returns the set of keys from the record's props to be used in the props body of the merge statements
        :param record:
        :param exclude_keys: set of excluded columns that do not need to be in properties (e.g: KEY, LABEL ...)
        """
        props_body_keys = set(record.keys()) - exclude_keys
        formatted_keys = map(self._strip_unquoted_suffix, props_body_keys)
        return set(formatted_keys).union(self._additional_publisher_metadata_fields.keys())

    def _create_props_body(self,
                           record_keys: Set,
                           identifier: str,
                           rename_id_to_preserve_ui_data: bool = False) -> str:
        """
        Creates properties body with params required for resolving template.

        e.g: Note that node.key3 is not quoted if header has UNQUOTED_SUFFIX.
        identifier.key1 = 'val1' , identifier.key2 = 'val2', identifier.key3 = val3

        :param record_keys: a list of keys for a CSV row
        :param identifier: identifier that will be used in CYPHER query as shown on above example
        :param rename_id_to_preserve_ui_data: specifies whether to null out the identifier to prevent it from updating
        :return: Properties body for Cypher statement
        """
        # For SET, if the evaluated expression is null, no action is performed. I.e. `SET (null).foo = 5` is a noop.
        # See https://neo4j.com/docs/cypher-manual/current/clauses/set/
        if rename_id_to_preserve_ui_data:
            identifier = f"""
                (CASE WHEN {identifier}.{PublisherConfigs.PUBLISHED_TAG_PROPERTY_NAME} IS NOT NULL
                THEN {identifier} ELSE null END)
            """

        template = Template("""
            {% for k in record_keys %}
                {{ identifier }}.{{ k }} = row.{{ k }}
                {{ ", " if not loop.last else "" }}
            {% endfor %}
            {% if record_keys and add_publisher_metadata %}
                , 
            {% endif %}
            {% if add_publisher_metadata %}
                {{ identifier }}.{{ published_tag_prop }} = '{{ publish_tag }}',
                {{ identifier }}.{{ last_updated_prop }} = timestamp()
            {% endif %}
        """)

        props_body = template.render(record_keys=record_keys,
                                     identifier=identifier,
                                     add_publisher_metadata=self._add_publisher_metadata,
                                     published_tag_prop=PublisherConfigs.PUBLISHED_TAG_PROPERTY_NAME,
                                     publish_tag=self._publish_tag,
                                     last_updated_prop=PublisherConfigs.LAST_UPDATED_EPOCH_MS)
        return props_body.strip()

    def _execute_statement(self,
                           tx: Transaction,
                           stmt: str,
                           params: dict) -> None:
        """
        Executes statement against Neo4j. If execution fails, it rollsback and raise exception.
        :param tx:
        :param stmt:
        :param params:
        :return:
        """

        LOGGER.debug('Executing statement: %s with params %s', stmt, params)

        tx.run(stmt, parameters=params)

        self._count += len(params['batch'])
        LOGGER.info(f'Committed {self._count} rows so far')

    def _try_create_index(self, tx: Transaction, label: str) -> None:
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

        tx.run(stmt)
