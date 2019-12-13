"""
This is a example script which demo how to load data into neo4j without using Airflow DAG.
"""

import logging
import os
from pyhocon import ConfigFactory
from urllib import unquote_plus

from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.extractor.snowflake_metadata_extractor import SnowflakeMetadataExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from databuilder.task.task import DefaultTask

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
# Disable snowflake logging
logging.getLogger("snowflake.connector.network").disabled = True

SNOWFLAKE_CONN_STRING = 'snowflake://username:%s@account' % unquote_plus('password')

# set env NEO4J_HOST to override localhost
NEO4J_ENDPOINT = 'bolt://{}:7687'.format(os.getenv('NEO4J_HOST', 'localhost'))
neo4j_endpoint = NEO4J_ENDPOINT

neo4j_user = 'neo4j'
neo4j_password = 'test'

IGNORED_SCHEMAS = ['\'DVCORE\'', '\'INFORMATION_SCHEMA\'', '\'STAGE_ORACLE\'']


def create_sample_snowflake_job():

    where_clause = "WHERE c.TABLE_SCHEMA not in ({0}) \
            AND c.TABLE_SCHEMA not like 'STAGE_%' \
            AND c.TABLE_SCHEMA not like 'HIST_%' \
            AND c.TABLE_SCHEMA not like 'SNAP_%' \
            AND lower(c.COLUMN_NAME) not like 'dw_%';".format(','.join(IGNORED_SCHEMAS))

    tmp_folder = '/var/tmp/amundsen/{}'.format('tables')
    node_files_folder = '{tmp_folder}/nodes'.format(tmp_folder=tmp_folder)
    relationship_files_folder = '{tmp_folder}/relationships'.format(tmp_folder=tmp_folder)

    sql_extractor = SnowflakeMetadataExtractor()
    csv_loader = FsNeo4jCSVLoader()

    task = DefaultTask(extractor=sql_extractor,
                       loader=csv_loader)

    job_config = ConfigFactory.from_dict({
        'extractor.snowflake.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): SNOWFLAKE_CONN_STRING,
        'extractor.snowflake.{}'.format(SnowflakeMetadataExtractor.DATABASE_KEY): 'YourSnowflakeDbName',
        'extractor.snowflake.{}'.format(SnowflakeMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY): where_clause,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH): node_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH): relationship_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR): True,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.FORCE_CREATE_DIR): True,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NODE_FILES_DIR): node_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.RELATION_FILES_DIR): relationship_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_END_POINT_KEY): neo4j_endpoint,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_USER): neo4j_user,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_PASSWORD): neo4j_password,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.JOB_PUBLISH_TAG): 'unique_tag'
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=Neo4jCsvPublisher())
    return job


if __name__ == "__main__":
    job = create_sample_snowflake_job()
    job.launch()
