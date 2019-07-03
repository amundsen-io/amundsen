"""
This is a example script which demo how to load data
into Neo4j and Elasticsearch without using an Airflow DAG.
"""

import csv
from elasticsearch import Elasticsearch
import logging
from pyhocon import ConfigFactory
import sqlite3
from sqlalchemy.ext.declarative import declarative_base
import textwrap
import uuid

from databuilder.extractor.neo4j_es_last_updated_extractor import Neo4jEsLastUpdatedExtractor
from databuilder.extractor.neo4j_search_data_extractor import Neo4jSearchDataExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from databuilder.publisher.elasticsearch_publisher import ElasticsearchPublisher
from databuilder.task.task import DefaultTask
from databuilder.transformer.base_transformer import NoopTransformer

# change to the address of Elasticsearch service
es = Elasticsearch([
    {'host': 'localhost'},
])

DB_FILE = '/tmp/test.db'
SQLITE_CONN_STRING = 'sqlite:////tmp/test.db'
Base = declarative_base()

# replace localhost with docker host ip
# todo: get the ip from input argument
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


def load_user_data_from_csv(file_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_user_metadata')
        cur.execute('create table if not exists test_user_metadata '
                    '(email VARCHAR(64) NOT NULL , '
                    'first_name VARCHAR(64) NOT NULL , '
                    'last_name VARCHAR(64) NOT NULL , '
                    'name VARCHAR(64) NOT NULL , '
                    'github_username VARCHAR(64) NOT NULL , '
                    'team_name VARCHAR(64) NOT NULL, '
                    'employee_type VARCHAR(64) NOT NULL,'
                    'manager_email VARCHAR(64) NOT NULL,'
                    'slack_id VARCHAR(64) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['email'],
                      i['first_name'],
                      i['last_name'],
                      i['name'],
                      i['github_username'],
                      i['team_name'],
                      i['employee_type'],
                      i['manager_email'],
                      i['slack_id']) for i in dr]

        cur.executemany("INSERT INTO test_user_metadata ("
                        "email, first_name, last_name, name, github_username, "
                        "team_name, employee_type, "
                        "manager_email, slack_id ) VALUES "
                        "(?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
        conn.commit()


def load_application_data_from_csv(file_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_application_metadata')
        cur.execute('create table if not exists test_application_metadata '
                    '(task_id VARCHAR(64) NOT NULL , '
                    'dag_id VARCHAR(64) NOT NULL , '
                    'exec_date VARCHAR(64) NOT NULL, '
                    'application_url_template VARCHAR(128) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['task_id'],
                      i['dag_id'],
                      i['exec_date'],
                      i['application_url_template']) for i in dr]

        cur.executemany("INSERT INTO test_application_metadata (task_id, dag_id, "
                        "exec_date, application_url_template) VALUES (?, ?, ?, ?);", to_db)
        conn.commit()


# todo: Add a second model
def create_sample_job(table_name, model_name, transformer=NoopTransformer()):
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
                       transformer=transformer)

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
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.JOB_PUBLISH_TAG):
            'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=Neo4jCsvPublisher())
    return job


def load_usage_data_from_csv(file_name):
    # Load usage data
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_usage_metadata')
        cur.execute('create table if not exists test_usage_metadata '
                    '(database VARCHAR(64) NOT NULL , '
                    'cluster VARCHAR(64) NOT NULL, '
                    'schema_name VARCHAR(64) NOT NULL, '
                    'table_name VARCHAR(64) NOT NULL, '
                    'column_name VARCHAR(64) NOT NULL, '
                    'user_email VARCHAR(64) NOT NULL, '
                    'read_count INTEGER NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['database'],
                      i['cluster'],
                      i['schema_name'],
                      i['table_name'],
                      i['column_name'],
                      i['user_email'],
                      i['read_count']
                      ) for i in dr]

        cur.executemany("INSERT INTO test_usage_metadata (database, cluster, "
                        "schema_name, table_name, column_name, user_email, read_count) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?);", to_db)
        conn.commit()


def create_last_updated_job():
    # loader saves data to these folders and publisher reads it from here
    tmp_folder = '/var/tmp/amundsen/last_updated_data'
    node_files_folder = '{tmp_folder}/nodes'.format(tmp_folder=tmp_folder)
    relationship_files_folder = '{tmp_folder}/relationships'.format(tmp_folder=tmp_folder)

    task = DefaultTask(extractor=Neo4jEsLastUpdatedExtractor(),
                       loader=FsNeo4jCSVLoader())

    job_config = ConfigFactory.from_dict({
        'extractor.neo4j_es_last_updated.model_class':
            'databuilder.models.neo4j_es_last_updated.Neo4jESLastUpdated',

        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH):
            node_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH):
            relationship_files_folder,

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
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.JOB_PUBLISH_TAG):
            'unique_lastupdated_tag',  # should use unique tag here like {ds}
    })

    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=Neo4jCsvPublisher())
    return job


def create_es_publisher_sample_job():
    # loader saves data to this location and publisher reads it from here
    extracted_search_data_path = '/var/tmp/amundsen/search_data.json'

    task = DefaultTask(loader=FSElasticsearchJSONLoader(),
                       extractor=Neo4jSearchDataExtractor(),
                       transformer=NoopTransformer())

    # elastic search client instance
    elasticsearch_client = es
    # unique name of new index in Elasticsearch
    elasticsearch_new_index_key = 'tables' + str(uuid.uuid4())
    # related to mapping type from /databuilder/publisher/elasticsearch_publisher.py#L38
    elasticsearch_new_index_key_type = 'table'
    # alias for Elasticsearch used in amundsensearchlibrary/search_service/config.py as an index
    elasticsearch_index_alias = 'table_search_index'

    job_config = ConfigFactory.from_dict({
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.GRAPH_URL_CONFIG_KEY): neo4j_endpoint,
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY):
            'databuilder.models.table_elasticsearch_document.TableESDocument',
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_USER): neo4j_user,
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_PW): neo4j_password,
        'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_PATH_CONFIG_KEY):
            extracted_search_data_path,
        'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_MODE_CONFIG_KEY): 'w',
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_PATH_CONFIG_KEY):
            extracted_search_data_path,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_MODE_CONFIG_KEY): 'r',
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_CLIENT_CONFIG_KEY):
            elasticsearch_client,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY):
            elasticsearch_new_index_key,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_DOC_TYPE_CONFIG_KEY):
            elasticsearch_new_index_key_type,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_ALIAS_CONFIG_KEY):
            elasticsearch_index_alias
    })

    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=ElasticsearchPublisher())
    return job


if __name__ == "__main__":
    # Uncomment next line to get INFO level logging
    # logging.basicConfig(level=logging.INFO)

    load_table_data_from_csv('sample_table.csv')
    load_col_data_from_csv('sample_col.csv')
    load_usage_data_from_csv('sample_column_usage.csv')
    load_user_data_from_csv('sample_user.csv')
    load_application_data_from_csv('sample_application.csv')
    if create_connection(DB_FILE):
        # start table job
        job1 = create_sample_job('test_table_metadata',
                                 'databuilder.models.table_metadata.TableMetadata')
        job1.launch()

        # start col job
        job2 = create_sample_job('test_col_metadata',
                                 'example.models.test_column_model.TestColumnMetadata')
        job2.launch()

        # start usage job
        job_col_usage = create_sample_job('test_usage_metadata',
                                          'example.models.test_column_usage_model.TestColumnUsageModel')
        job_col_usage.launch()

        # start user job
        job_user = create_sample_job('test_user_metadata',
                                     'databuilder.models.user.User')
        job_user.launch()

        # start application job
        job_app = create_sample_job('test_application_metadata',
                                    'databuilder.models.application.Application')
        job_app.launch()

        # start last updated job
        job_lastupdated = create_last_updated_job()
        job_lastupdated.launch()

        # start Elasticsearch publish job
        job_es = create_es_publisher_sample_job()
        job_es.launch()
