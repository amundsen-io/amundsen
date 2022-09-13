# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import csv
import ctypes
import logging
import time
from io import open
from typing import (
    Dict, List, Set,
)

import neo4j
import pandas
from jinja2 import Template
from neo4j import GraphDatabase, Neo4jDriver
from neo4j.api import (
    SECURITY_TYPE_SECURE, SECURITY_TYPE_SELF_SIGNED_CERTIFICATE, parse_neo4j_uri,
)
from pyhocon import ConfigFactory, ConfigTree

from databuilder.models.graph_serializable import (
    NODE_KEY, NODE_LABEL, RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY,
    RELATION_START_LABEL, RELATION_TYPE,
)
from databuilder.publisher.base_publisher import Publisher
from databuilder.publisher.publisher_config_constants import (
    Neo4jCsvPublisherConfigs, PublishBehaviorConfigs, PublisherConfigs,
)
from databuilder.utils.publisher_utils import (
    chunkify_list, create_neo4j_node_key_constraint, create_props_param, execute_neo4j_statement, get_props_body_keys,
    list_files,
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

DEFAULT_CONFIG = ConfigFactory.from_dict({Neo4jCsvPublisherConfigs.NEO4J_TRANSACTION_SIZE: 1000,
                                          Neo4jCsvPublisherConfigs.NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
                                          Neo4jCsvPublisherConfigs.NEO4J_DATABASE_NAME: neo4j.DEFAULT_DATABASE,
                                          PublishBehaviorConfigs.ADD_PUBLISHER_METADATA: True,
                                          PublishBehaviorConfigs.PUBLISH_REVERSE_RELATIONSHIPS: True,
                                          PublishBehaviorConfigs.PRESERVE_ADHOC_UI_DATA: True,
                                          PublishBehaviorConfigs.PRESERVE_EMPTY_PROPS: True})

LOGGER = logging.getLogger(__name__)


class Neo4jCsvUnwindPublisher(Publisher):
    """
    This publisher takes two folders for input and publishes to Neo4j.
    One folder will contain CSV file(s) for Nodes where the other folder will contain CSV
    file(s) for Relationships.

    The merge statements make use of the UNWIND clause to allow for batched params to be applied to each
    statement. This improves performance by reducing the amount of individual transactions to the database,
    and by allowing Neo4j to compile and cache the statement.
    """

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(DEFAULT_CONFIG)

        self._count: int = 0
        self._node_files = list_files(conf, PublisherConfigs.NODE_FILES_DIR)
        self._node_files_iter = iter(self._node_files)

        self._relation_files = list_files(conf, PublisherConfigs.RELATION_FILES_DIR)
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
            dict(conf.get(PublisherConfigs.ADDITIONAL_PUBLISHER_METADATA_FIELDS, default={}))
        self._add_publisher_metadata: bool = conf.get_bool(PublishBehaviorConfigs.ADD_PUBLISHER_METADATA)
        self._publish_reverse_relationships: bool = conf.get_bool(PublishBehaviorConfigs.PUBLISH_REVERSE_RELATIONSHIPS)
        self._preserve_adhoc_ui_data = conf.get_bool(PublishBehaviorConfigs.PRESERVE_ADHOC_UI_DATA)
        self._preserve_empty_props: bool = conf.get_bool(PublishBehaviorConfigs.PRESERVE_EMPTY_PROPS)
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

        driver = GraphDatabase.driver(**driver_args)

        try:
            driver.verify_connectivity()
        except Exception as e:
            driver.close()
            raise e

        return driver

    def publish_impl(self) -> None:  # noqa: C901
        """
        Publishes Nodes first and then Relations
        """
        start = time.time()

        for node_file in self._node_files:
            self.pre_publish_node_file(node_file)

        LOGGER.info('Publishing Node files: %s', self._node_files)
        while True:
            try:
                node_file = next(self._node_files_iter)
                self._publish_node_file(node_file)
            except StopIteration:
                break

        for rel_file in self._relation_files:
            self.pre_publish_rel_file(rel_file)

        LOGGER.info('Publishing Relationship files: %s', self._relation_files)
        while True:
            try:
                relation_file = next(self._relation_files_iter)
                self._publish_relation_file(relation_file)
            except StopIteration:
                break

        LOGGER.info('Committed total %i statements', self._count)

        # TODO: Add statsd support
        LOGGER.info('Successfully published. Elapsed: %i seconds', time.time() - start)

    def get_scope(self) -> str:
        return 'publisher.neo4j'

    # Can be overridden with custom action(s)
    def pre_publish_node_file(self, node_file: str) -> None:
        created_constraint_labels = create_neo4j_node_key_constraint(node_file, self._labels,
                                                                     self._driver, self._db_name)
        self._labels.union(created_constraint_labels)

    # Can be overridden with custom action(s)
    def pre_publish_rel_file(self, rel_file: str) -> None:
        pass

    def _publish_node_file(self, node_file: str) -> None:
        with open(node_file, 'r', encoding='utf8') as node_csv:
            csv_dataframe = pandas.read_csv(node_csv, na_filter=False)
            all_node_records = csv_dataframe.to_dict(orient="records")

            # Get the first node label since they will be the same for all records in the file
            merge_stmt = self._create_node_merge_statement(node_keys=csv_dataframe.columns.tolist(),
                                                           node_label=all_node_records[0][NODE_LABEL])

            self._write_transactions(merge_stmt, all_node_records)

    def _create_node_merge_statement(self, node_keys: list, node_label: str) -> str:
        template = Template("""
            UNWIND $batch AS row
            MERGE (node:{{ LABEL }} {key: row.KEY})
            ON CREATE SET {{ PROPS_BODY_CREATE }}
            {% if update %} ON MATCH SET {{ PROPS_BODY_UPDATE }} {% endif %}
        """)

        props_body_create = self._create_props_body(get_props_body_keys(node_keys,
                                                    NODE_REQUIRED_KEYS,
                                                    self._additional_publisher_metadata_fields), 'node')

        props_body_update = props_body_create
        if self._preserve_adhoc_ui_data:
            props_body_update = self._create_props_body(get_props_body_keys(node_keys,
                                                                            NODE_REQUIRED_KEYS,
                                                                            self._additional_publisher_metadata_fields),
                                                        'node', True)

        return template.render(LABEL=node_label,
                               PROPS_BODY_CREATE=props_body_create,
                               PROPS_BODY_UPDATE=props_body_update,
                               update=(node_label not in self._create_only_nodes))

    def _publish_relation_file(self, relation_file: str) -> None:
        with open(relation_file, 'r', encoding='utf8') as relation_csv:
            csv_dataframe = pandas.read_csv(relation_csv, na_filter=False)
            all_rel_records = csv_dataframe.to_dict(orient="records")

            # Get the first relation labels since they will be the same for all records in the file
            merge_stmt = self._create_relationship_merge_statement(
                rel_keys=csv_dataframe.columns.tolist(),
                start_label=all_rel_records[0][RELATION_START_LABEL],
                end_label=all_rel_records[0][RELATION_END_LABEL],
                relation_type=all_rel_records[0][RELATION_TYPE],
                relation_reverse_type=all_rel_records[0][RELATION_REVERSE_TYPE]
            )

            self._write_transactions(merge_stmt, all_rel_records)

    def _create_relationship_merge_statement(self,
                                             rel_keys: list,
                                             start_label: str,
                                             end_label: str,
                                             relation_type: str,
                                             relation_reverse_type: str) -> str:
        template = Template("""
            UNWIND $batch as row
            MATCH (n1:{{ START_LABEL }} {key: row.START_KEY}), (n2:{{ END_LABEL }} {key: row.END_KEY})
            {% if publish_reverse_relationships %}
            MERGE (n1)-[r1:{{ TYPE }}]->(n2)-[r2:{{ REVERSE_TYPE }}]->(n1)
            {% elif not publish_reverse_relationships and has_key %}
            MERGE (n1)-[r1:{{ TYPE }} {key: row.key}]->(n2)
            {% else %}
            MERGE (n1)-[r1:{{ TYPE }}]->(n2)
            {% endif %}
            {% if update_props_body %}
            ON CREATE SET {{ props_body_create }}
            ON MATCH SET {{ props_body_update }}
            {% endif %}
            RETURN n1.key, n2.key
        """)

        props_body_template = Template("""{{ props_body_r1 }} , {{ props_body_r2 }}""")

        props_body_r1 = self._create_props_body(get_props_body_keys(rel_keys,
                                                                    RELATION_REQUIRED_KEYS,
                                                                    self._additional_publisher_metadata_fields), 'r1')
        props_body_r2 = self._create_props_body(get_props_body_keys(rel_keys,
                                                                    RELATION_REQUIRED_KEYS,
                                                                    self._additional_publisher_metadata_fields), 'r2')
        if self._publish_reverse_relationships:
            props_body_create = props_body_template.render(props_body_r1=props_body_r1, props_body_r2=props_body_r2)
        else:
            props_body_create = props_body_r1

        props_body_update = props_body_create
        if self._preserve_adhoc_ui_data:
            props_body_r1 = self._create_props_body(get_props_body_keys(rel_keys,
                                                                        RELATION_REQUIRED_KEYS,
                                                                        self._additional_publisher_metadata_fields),
                                                    'r1', True)
            props_body_r2 = self._create_props_body(get_props_body_keys(rel_keys,
                                                                        RELATION_REQUIRED_KEYS,
                                                                        self._additional_publisher_metadata_fields),
                                                    'r2', True)
            if self._publish_reverse_relationships:
                props_body_update = props_body_template.render(props_body_r1=props_body_r1, props_body_r2=props_body_r2)
            else:
                props_body_update = props_body_r1

        return template.render(START_LABEL=start_label,
                               END_LABEL=end_label,
                               publish_reverse_relationships=self._publish_reverse_relationships,
                               has_key='key' in rel_keys,
                               TYPE=relation_type,
                               REVERSE_TYPE=relation_reverse_type,
                               update_props_body=props_body_r1,
                               props_body_create=props_body_create,
                               props_body_update=props_body_update)

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
                {% if preserve_empty_props %}
                    {{ identifier }}.{{ k }} = row.{{ k }}
                {% else %}
                    {{ identifier }}.{{ k }} = (CASE row.{{ k }} WHEN '' THEN NULL ELSE row.{{ k }} END)
                {% endif %}
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
                                     preserve_empty_props=self._preserve_empty_props,
                                     identifier=identifier,
                                     add_publisher_metadata=self._add_publisher_metadata,
                                     published_tag_prop=PublisherConfigs.PUBLISHED_TAG_PROPERTY_NAME,
                                     publish_tag=self._publish_tag,
                                     last_updated_prop=PublisherConfigs.LAST_UPDATED_EPOCH_MS)
        return props_body.strip()

    def _write_transactions(self,
                            stmt: str,
                            records: List[dict]) -> None:
        for chunk in chunkify_list(records, self._transaction_size):
            params_list = []
            for record in chunk:
                params_list.append(create_props_param(record, self._additional_publisher_metadata_fields))

            with self._driver.session(database=self._db_name) as session:
                session.write_transaction(execute_neo4j_statement, stmt, {'batch': params_list})

                self._count += len(params_list)
                LOGGER.info(f'Committed {self._count} rows so far')
