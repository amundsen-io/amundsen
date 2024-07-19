# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

"""
This is a example script which demo how to load data
into Neo4j and Elasticsearch without using an Airflow DAG.

"""

import logging
import sys
import textwrap
import os

from elasticsearch import Elasticsearch
from pyhocon import ConfigFactory
from sqlalchemy.ext.declarative import declarative_base

from databuilder.extractor.redshift_metadata_extractor import RedshiftMetadataExtractor
from databuilder.extractor.redshift_table_last_updated_extractor import RedshiftTableLastUpdatedExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from databuilder.task.task import DefaultTask
from databuilder.transformer.base_transformer import NoopTransformer

es_host = None
neo_host = None
if len(sys.argv) > 1:
    es_host = sys.argv[1]
if len(sys.argv) > 2:
    neo_host = sys.argv[2]

es = Elasticsearch([
    {'host': es_host if es_host else 'localhost'},
])

DB_FILE = '/tmp/test.db'
SQLITE_CONN_STRING = 'sqlite:////tmp/test.db'
Base = declarative_base()

NEO4J_ENDPOINT = f'bolt://{neo_host or "localhost"}:7687'

neo4j_endpoint = NEO4J_ENDPOINT

neo4j_user = 'neo4j'
neo4j_password = 'test'

LOGGER = logging.getLogger(__name__)

# todo: connection string needs to change
def connection_string():
    user = 'username'
    host = 'hostname.aws.com'
    port = 5439
    db = 'public'
    password = 'mypasswors'
    return "postgresql://%s:%s@%s:%s/%s" % (user, password, host, port, db)


def run_redshift_table_model_job():
    where_clause_suffix = textwrap.dedent("""
        WHERE schema = 'myschema'
    """)

    tmp_folder = os.path.join(os.getcwd(), 'amundsen', 'table_metadata')
    node_files_folder = os.path.join(tmp_folder, 'nodes')
    relationship_files_folder = os.path.join(tmp_folder, 'relationships')

    task = DefaultTask(
        extractor=RedshiftMetadataExtractor(),
        loader=FsNeo4jCSVLoader(),
        transformer=NoopTransformer()
    )

    job_config = ConfigFactory.from_dict({
        f'extractor.redshift_metadata.{RedshiftMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY}': where_clause_suffix,
        f'extractor.redshift_metadata.{RedshiftMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME}': True,
        f'extractor.redshift_metadata.extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}': connection_string(),
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': node_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': relationship_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR}': True,
        f'publisher.neo4j.{neo4j_csv_publisher.NODE_FILES_DIR}': node_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.RELATION_FILES_DIR}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_END_POINT_KEY}': neo4j_endpoint,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_USER}': neo4j_user,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_PASSWORD}': neo4j_password,
        f'publisher.neo4j.{neo4j_csv_publisher.JOB_PUBLISH_TAG}': 'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(
        conf=job_config,
        task=task,
        publisher=Neo4jCsvPublisher()
    )
    return job


def run_redshift_table_last_updated_job():
    where_clause_suffix = textwrap.dedent("""
        WHERE schema = 'myschema'
    """)

    tmp_folder = os.path.join(os.getcwd(), 'amundsen', 'last_updated_data')
    node_files_folder = os.path.join(tmp_folder, 'nodes')
    relationship_files_folder = os.path.join(tmp_folder, 'relationships')

    task = DefaultTask(
        extractor=RedshiftTableLastUpdatedExtractor(),
        loader=FsNeo4jCSVLoader(),
        transformer=NoopTransformer()
    )

    job_config = ConfigFactory.from_dict({
        f'extractor.redshift_table_last_updated.{RedshiftTableLastUpdatedExtractor.WHERE_CLAUSE_SUFFIX_KEY}': where_clause_suffix,
        f'extractor.redshift_table_last_updated.{RedshiftTableLastUpdatedExtractor.USE_CATALOG_AS_CLUSTER_NAME}': True,
        f'extractor.redshift_table_last_updated.extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}': connection_string(),
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': node_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': relationship_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR}': True,
        f'publisher.neo4j.{neo4j_csv_publisher.NODE_FILES_DIR}': node_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.RELATION_FILES_DIR}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_END_POINT_KEY}': neo4j_endpoint,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_USER}': neo4j_user,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_PASSWORD}': neo4j_password,
        f'publisher.neo4j.{neo4j_csv_publisher.JOB_PUBLISH_TAG}': 'unique_tag' # should use unique tag here like {ds}
    })
    job = DefaultJob(
        conf=job_config,
        task=task,
        publisher=Neo4jCsvPublisher()
    )
    return job

if __name__ == "__main__":
    # Uncomment next line to get INFO level logging
    # logging.basicConfig(level=logging.INFO)

    loading_job1 = run_redshift_table_model_job()
    loading_job1.launch()

    loading_job2 = run_redshift_table_last_updated_job()
    loading_job2.launch()
