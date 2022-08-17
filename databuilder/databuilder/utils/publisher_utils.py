# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from os import listdir
from os.path import isfile, join
from typing import (
    Iterator, List, Set,
)

import pandas
from jinja2 import Template
from neo4j import Neo4jDriver, Transaction
from neo4j.exceptions import Neo4jError
from pyhocon import ConfigTree

from databuilder.models.graph_serializable import NODE_LABEL
from databuilder.publisher.publisher_config_constants import PublisherConfigs

LOGGER = logging.getLogger(__name__)

NEO4J_EQUIVALENT_SCHEMA_RULE_ALREADY_EXISTS_ERROR_CODE = 'Neo.ClientError.Schema.EquivalentSchemaRuleAlreadyExists'
NEO4J_INDEX_ALREADY_EXISTS_ERROR_CODE = 'Neo.ClientError.Schema.IndexWithNameAlreadyExists'


def chunkify_list(records: List[dict], chunk_size: int) -> Iterator[List[dict]]:
    """
    Generator to evenly split the input list into chunks
    """
    for index in range(0, len(records), chunk_size):
        yield records[index:index + chunk_size]


def create_neo4j_node_key_constraint(node_file: str,
                                     current_labels: Set,
                                     driver: Neo4jDriver,
                                     db_name: str) -> Set:
    """
    Go over the node file and try creating unique indices.
    For any label seen first time for this publisher it will try to create unique index.
    Neo4j ignores a second creation in 3.x, but raises an error in 4.x.
    """
    LOGGER.info('Creating indices using Node file: %s. (Existing indices will be ignored)', node_file)

    labels = set(current_labels)
    with open(node_file, 'r', encoding='utf8') as node_csv:
        for node_record in pandas.read_csv(node_csv,
                                           na_filter=False).to_dict(orient='records'):
            label = node_record[NODE_LABEL]
            if label not in labels:
                with driver.session(database=db_name) as session:
                    try:
                        create_stmt = Template("""
                            CREATE CONSTRAINT ON (node:{{ LABEL }}) ASSERT node.key IS UNIQUE
                        """).render(LABEL=label)

                        LOGGER.info(f'Trying to create index for label {label} if not exist: {create_stmt}')

                        session.write_transaction(execute_neo4j_statement, create_stmt)
                    except Neo4jError as e:
                        if e.code != NEO4J_EQUIVALENT_SCHEMA_RULE_ALREADY_EXISTS_ERROR_CODE\
                                and e.code != NEO4J_INDEX_ALREADY_EXISTS_ERROR_CODE:
                            raise
                        # Else, swallow the exception, to make this function idempotent.
                labels.add(label)

    LOGGER.info('Indices have been created.')
    return labels


def create_props_param(record_dict: dict, additional_publisher_metadata_fields: dict) -> dict:
    """
    Create a dict of all the params for a given record
    """
    params = {}

    for k, v in {**record_dict, **additional_publisher_metadata_fields}.items():
        params[strip_unquoted_suffix(k)] = v

    return params


def execute_neo4j_statement(tx: Transaction,
                            stmt: str,
                            params: dict = None) -> None:
    """
    Executes statement against Neo4j. If execution fails, it rollsback and raises exception.
    """
    LOGGER.debug('Executing statement: %s with params %s', stmt, params)

    tx.run(stmt, parameters=params)


def get_props_body_keys(record_keys: list,
                        exclude_keys: Set,
                        additional_publisher_metadata_fields: dict) -> Set:
    """
    Returns the set of keys to be used in the props body of the merge statements
    :param record_keys:
    :param exclude_keys: set of excluded columns that do not need to be in properties (e.g: KEY, LABEL ...)
    :param additional_publisher_metadata_fields:
    """
    props_body_keys = set(record_keys) - exclude_keys
    formatted_keys = map(strip_unquoted_suffix, props_body_keys)
    return set(formatted_keys).union(additional_publisher_metadata_fields.keys())


def list_files(conf: ConfigTree, path_key: str) -> List[str]:
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


def strip_unquoted_suffix(key: str) -> str:
    return key[:-len(PublisherConfigs.UNQUOTED_SUFFIX)] if key.endswith(PublisherConfigs.UNQUOTED_SUFFIX) else key
