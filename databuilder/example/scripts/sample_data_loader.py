"""
This is a example script which demo how to load data into neo4j without using Airflow DAG.
"""

import csv
import logging
from pyhocon import ConfigFactory
import sqlite3
from sqlalchemy.ext.declarative import declarative_base
import textwrap

from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from databuilder.task.task import DefaultTask
from databuilder.transformer.base_transformer import NoopTransformer


DB_FILE = '/tmp/test.db'
SQLITE_CONN_STRING = 'sqlite:////tmp/test.db'
Base = declarative_base()

NEO4J_ENDPOINT = 'bolt://localhost:7687'
neo4j_endpoint = NEO4J_ENDPOINT

neo4j_user = 'neo4j'
neo4j_password = 'test'


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception:
        logging.exception('exception')
    return None


def load_table_data_from_csv(file_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_table_metadata')
        cur.execute('create table if not exists test_table_metadata '
                    '(database VARCHAR(64) NOT NULL , '
                    'cluster VARCHAR(64) NOT NULL, '
                    'schema_name VARCHAR(64) NOT NULL,'
                    'name VARCHAR(64) NOT NULL,'
                    'description VARCHAR(64) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['database'],
                      i['cluster'],
                      i['schema_name'],
                      i['table_name'],
                      i['table_desc']) for i in dr]

        cur.executemany("INSERT INTO test_table_metadata (database, cluster, "
                        "schema_name, name, description) VALUES (?, ?, ?, ?, ?);", to_db)
        conn.commit()


def load_col_data_from_csv(file_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_col_metadata')
        cur.execute('create table if not exists test_col_metadata '
                    '(name VARCHAR(64) NOT NULL , '
                    'description VARCHAR(64) NOT NULL , '
                    'col_type VARCHAR(64) NOT NULL , '
                    'sort_order INTEGER NOT NULL , '
                    'database VARCHAR(64) NOT NULL , '
                    'cluster VARCHAR(64) NOT NULL, '
                    'schema_name VARCHAR(64) NOT NULL,'
                    'table_name VARCHAR(64) NOT NULL,'
                    'table_description VARCHAR(64) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['name'],
                      i['description'],
                      i['col_type'],
                      i['sort_order'],
                      i['database'],
                      i['cluster'],
                      i['schema_name'],
                      i['table_name'],
                      i['table_desc']) for i in dr]

        cur.executemany("INSERT INTO test_col_metadata ("
                        "name, description, col_type, sort_order,"
                        "database, cluster, "
                        "schema_name, table_name, table_description) VALUES "
                        "(?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
        conn.commit()


# todo: Add a second model
def create_sample_job(table_name, model_name):
    sql = textwrap.dedent("""
    select * from {table_name};
    """).format(table_name=table_name)

    tmp_folder = '/var/tmp/amundsen/{table_name}'.format(table_name=table_name)
    node_files_folder = '{tmp_folder}/nodes'.format(tmp_folder=tmp_folder)
    relationship_files_folder = '{tmp_folder}/relationships'.format(tmp_folder=tmp_folder)

    sql_extractor = SQLAlchemyExtractor()
    csv_loader = FsNeo4jCSVLoader()

    task = DefaultTask(extractor=sql_extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())

    job_config = ConfigFactory.from_dict({
        'extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): SQLITE_CONN_STRING,
        'extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.EXTRACT_SQL): sql,
        'extractor.sqlalchemy.model_class': model_name,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH):
            node_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH):
            relationship_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR):
            True,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NODE_FILES_DIR):
            node_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.RELATION_FILES_DIR):
            relationship_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_END_POINT_KEY):
            neo4j_endpoint,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_USER):
            neo4j_user,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_PASSWORD):
            neo4j_password,
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=Neo4jCsvPublisher())
    return job


if __name__ == "__main__":
    load_table_data_from_csv('sample_table.csv')
    load_col_data_from_csv('sample_col.csv')
    if create_connection(DB_FILE):
        # start table job
        job1 = create_sample_job('test_table_metadata',
                                 'databuilder.models.table_metadata.TableMetadata')
        job1.launch()

        # start col job
        job2 = create_sample_job('test_col_metadata',
                                 'example.models.test_column_model.TestColumnMetadata')
        job2.launch()
