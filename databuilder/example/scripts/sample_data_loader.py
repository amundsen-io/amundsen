"""
This is a example script which demo how to load data
into Neo4j and Elasticsearch without using an Airflow DAG.
"""

import csv

import sys
from elasticsearch import Elasticsearch
import logging
from pyhocon import ConfigFactory
import sqlite3
from sqlalchemy.ext.declarative import declarative_base
import textwrap
import uuid
from collections import defaultdict

from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.neo4j_es_last_updated_extractor import Neo4jEsLastUpdatedExtractor
from databuilder.extractor.neo4j_search_data_extractor import Neo4jSearchDataExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from databuilder.publisher import neo4j_csv_publisher
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from databuilder.publisher.elasticsearch_publisher import ElasticsearchPublisher
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

NEO4J_ENDPOINT = 'bolt://{}:7687'.format(neo_host if neo_host else 'localhost')

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


def load_table_data_from_csv(file_name, table_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists {}'.format(table_name))
        cur.execute('create table if not exists {} '
                    '(database VARCHAR(64) NOT NULL , '
                    'cluster VARCHAR(64) NOT NULL, '
                    'schema VARCHAR(64) NOT NULL,'
                    'name VARCHAR(64) NOT NULL,'
                    'description VARCHAR(64) NOT NULL, '
                    'tags VARCHAR(128) NOT NULL,'
                    'description_source VARCHAR(32))'.format(table_name))
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['database'],
                      i['cluster'],
                      i['schema'],
                      i['name'],
                      i['description'],
                      i['tags'],
                      i['description_source']) for i in dr]

        cur.executemany("INSERT INTO {} (database, cluster, "
                        "schema, name, description, tags, "
                        "description_source) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?);".format(table_name), to_db)
        conn.commit()


def load_tag_data_from_csv(file_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_tag_metadata')
        cur.execute('create table if not exists test_tag_metadata '
                    '(name VARCHAR(64) NOT NULL , '
                    'tag_type VARCHAR(64) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['name'],
                      i['tag_type']) for i in dr]

        cur.executemany("INSERT INTO test_tag_metadata (name, tag_type) VALUES (?, ?);", to_db)
        conn.commit()


def load_table_column_stats_from_csv(file_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_table_column_stats')
        cur.execute('create table if not exists test_table_column_stats '
                    '(cluster VARCHAR(64) NOT NULL , '
                    'db VARCHAR(64) NOT NULL , '
                    'schema VARCHAR(64) NOT NULL , '
                    'table_name INTEGER NOT NULL , '
                    'col_name VARCHAR(64) NOT NULL , '
                    'stat_name VARCHAR(64) NOT NULL, '
                    'stat_val VARCHAR(64) NOT NULL,'
                    'start_epoch VARCHAR(64) NOT NULL,'
                    'end_epoch VARCHAR(64) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['cluster'],
                      i['db'],
                      i['schema'],
                      i['table_name'],
                      i['col_name'],
                      i['stat_name'],
                      i['stat_val'],
                      i['start_epoch'],
                      i['end_epoch']) for i in dr]

        cur.executemany("INSERT INTO test_table_column_stats ("
                        "cluster, db, schema, table_name,"
                        "col_name, stat_name, "
                        "stat_val, start_epoch, end_epoch) VALUES "
                        "(?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
        conn.commit()


def load_watermark_data_from_csv(file_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_watermark_metadata')
        cur.execute('create table if not exists test_watermark_metadata '
                    '(create_time VARCHAR(64) NOT NULL , '
                    'database VARCHAR(64) NOT NULL , '
                    'schema VARCHAR(64) NOT NULL , '
                    'table_name VARCHAR(64) NOT NULL , '
                    'part_name VARCHAR(64) NOT NULL , '
                    'part_type VARCHAR(64) NOT NULL , '
                    'cluster VARCHAR(64) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = []
            for i in dr:
                to_db.append((i['create_time'],
                              i['database'],
                              i['schema'],
                              i['table_name'],
                              i['part_name'],
                              i['part_type'],
                              i['cluster']))

        cur.executemany("INSERT INTO test_watermark_metadata ("
                        "create_time, database, schema, table_name,"
                        "part_name, part_type, cluster) VALUES "
                        "(?, ?, ?, ?, ?, ?, ?);", to_db)
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
                    'full_name VARCHAR(64) NOT NULL , '
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
                      i['full_name'],
                      i['github_username'],
                      i['team_name'],
                      i['employee_type'],
                      i['manager_email'],
                      i['slack_id']) for i in dr]

        cur.executemany("INSERT INTO test_user_metadata ("
                        "email, first_name, last_name, full_name, github_username, "
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
                    'application_url_template VARCHAR(128) NOT NULL, '
                    'db_name VARCHAR(64) NOT NULL, '
                    'schema VARCHAR(64) NOT NULL, '
                    'table_name VARCHAR(64) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['task_id'],
                      i['dag_id'],
                      i['exec_date'],
                      i['application_url_template'],
                      i['db_name'],
                      i['schema'],
                      i['table_name'],) for i in dr]

        cur.executemany("INSERT INTO test_application_metadata (task_id, dag_id, "
                        "exec_date, application_url_template, db_name, schema, table_name) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?);", to_db)
        conn.commit()


def load_source_data_from_csv(file_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_source_metadata')
        cur.execute('create table if not exists test_source_metadata '
                    '(db_name VARCHAR(64) NOT NULL , '
                    'cluster VARCHAR(64) NOT NULL , '
                    'schema VARCHAR(64) NOT NULL, '
                    'table_name VARCHAR(64) NOT NULL, '
                    'source VARCHAR(64) NOT NULL , '
                    'source_type VARCHAR(32) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['db_name'],
                      i['cluster'],
                      i['schema'],
                      i['table_name'],
                      i['source'],
                      i['source_type']) for i in dr]

        cur.executemany("INSERT INTO test_source_metadata (db_name, cluster, "
                        "schema, table_name, source, source_type) VALUES (?, ?, ?, ?, ?, ?);", to_db)
        conn.commit()


def load_test_last_updated_data_from_csv(file_name):
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_table_last_updated_metadata')
        cur.execute('create table if not exists test_table_last_updated_metadata '
                    '(cluster VARCHAR(64) NOT NULL , '
                    'db VARCHAR(64) NOT NULL , '
                    'schema VARCHAR(64) NOT NULL, '
                    'table_name VARCHAR(64) NOT NULL, '
                    'last_updated_time_epoch LONG NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['cluster'],
                      i['db'],
                      i['schema'],
                      i['table_name'],
                      i['last_updated_time_epoch']) for i in dr]

        cur.executemany("INSERT INTO test_table_last_updated_metadata (cluster, db, "
                        "schema, table_name, last_updated_time_epoch) VALUES (?, ?, ?, ?, ?);", to_db)

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
                    '(database VARCHAR(64) NOT NULL, '
                    'cluster VARCHAR(64) NOT NULL, '
                    'schema VARCHAR(64) NOT NULL, '
                    'table_name VARCHAR(64) NOT NULL, '
                    'column_name VARCHAR(64) NOT NULL, '
                    'user_email VARCHAR(64) NOT NULL, '
                    'read_count INTEGER NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['database'],
                      i['cluster'],
                      i['schema'],
                      i['table_name'],
                      i['column_name'],
                      i['user_email'],
                      i['read_count']
                      ) for i in dr]

        cur.executemany("INSERT INTO test_usage_metadata (database, cluster, "
                        "schema, table_name, column_name, user_email, read_count) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?);", to_db)
        conn.commit()


def load_table_owner_data_from_csv(file_name):
    # Load usage data
    conn = create_connection(DB_FILE)
    if conn:
        cur = conn.cursor()
        cur.execute('drop table if exists test_table_owner_metadata')
        cur.execute('create table if not exists test_table_owner_metadata '
                    '(db_name VARCHAR(64) NOT NULL, '
                    'schema VARCHAR(64) NOT NULL, '
                    'table_name VARCHAR(64) NOT NULL, '
                    'owners VARCHAR(128) NOT NULL, '
                    'cluster VARCHAR(64) NOT NULL)')
        file_loc = 'example/sample_data/' + file_name
        with open(file_loc, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['db_name'],
                      i['schema'],
                      i['cluster'],
                      i['table_name'],
                      i['owners']
                      ) for i in dr]

        cur.executemany("INSERT INTO test_table_owner_metadata "
                        "(db_name, schema, cluster, table_name, owners) "
                        "VALUES (?, ?, ?, ?, ?);", to_db)
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
            'unique_last_updated_tag',  # should use unique tag here like {ds}
    })

    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=Neo4jCsvPublisher())
    return job


def create_es_publisher_sample_job(elasticsearch_index_alias='table_search_index',
                                   elasticsearch_doc_type_key='table',
                                   model_name='databuilder.models.table_elasticsearch_document.TableESDocument',
                                   cypher_query=None,
                                   elasticsearch_mapping=None):
    """
    :param elasticsearch_index_alias:  alias for Elasticsearch used in
                                       amundsensearchlibrary/search_service/config.py as an index
    :param elasticsearch_doc_type_key: name the ElasticSearch index is prepended with. Defaults to `table` resulting in
                                       `table_search_index`
    :param model_name:                 the Databuilder model class used in transporting between Extractor and Loader
    :param cypher_query:               Query handed to the `Neo4jSearchDataExtractor` class, if None is given (default)
                                       it uses the `Table` query baked into the Extractor
    :param elasticsearch_mapping:      Elasticsearch field mapping "DDL" handed to the `ElasticsearchPublisher` class,
                                       if None is given (default) it uses the `Table` query baked into the Publisher
    """
    # loader saves data to this location and publisher reads it from here
    extracted_search_data_path = '/var/tmp/amundsen/search_data.json'

    task = DefaultTask(loader=FSElasticsearchJSONLoader(),
                       extractor=Neo4jSearchDataExtractor(),
                       transformer=NoopTransformer())

    # elastic search client instance
    elasticsearch_client = es
    # unique name of new index in Elasticsearch
    elasticsearch_new_index_key = 'tables' + str(uuid.uuid4())

    job_config = ConfigFactory.from_dict({
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.GRAPH_URL_CONFIG_KEY): neo4j_endpoint,
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY): model_name,
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
            elasticsearch_doc_type_key,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_ALIAS_CONFIG_KEY):
            elasticsearch_index_alias,
    })

    # only optionally add these keys, so need to dynamically `put` them
    if cypher_query:
        job_config.put('extractor.search_data.{}'.format(Neo4jSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY),
                       cypher_query)
    if elasticsearch_mapping:
        job_config.put('publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_MAPPING_CONFIG_KEY),
                       elasticsearch_mapping)

    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=ElasticsearchPublisher())
    return job


class CSVTableColumnExtractor(Extractor):
    # Config keys
    TABLE_FILE_LOCATION = 'table_file_location'
    COLUMN_FILE_LOCATION = 'column_file_location'

    """
    An Extractor that combines Table and Column CSVs.
    """
    def init(self, conf):
        # type: (ConfigTree) -> None
        """
        :param conf:
        """
        self.conf = conf
        self.table_file_location = conf.get_string(CSVTableColumnExtractor.TABLE_FILE_LOCATION)
        self.column_file_location = conf.get_string(CSVTableColumnExtractor.COLUMN_FILE_LOCATION)
        self._load_csv()

    def _get_key(self, db, cluster, schema, tbl):
        return TableMetadata.TABLE_KEY_FORMAT.format(db=db,
                                                     cluster=cluster,
                                                     schema=schema,
                                                     tbl=tbl)

    def _load_csv(self):
        # type: () -> None
        """
        Create an iterator to execute sql.
        """

        with open(self.column_file_location, 'r') as fin:
            self.columns = [dict(i) for i in csv.DictReader(fin)]

        parsed_columns = defaultdict(list)
        for column_dict in self.columns:
            db = column_dict['database']
            cluster = column_dict['cluster']
            schema = column_dict['schema']
            table = column_dict['table_name']
            id = self._get_key(db, cluster, schema, table)
            column = ColumnMetadata(
                name=column_dict['name'],
                description=column_dict['description'],
                col_type=column_dict['col_type'],
                sort_order=int(column_dict['sort_order'])
            )
            parsed_columns[id].append(column)

        # Create Table Dictionary
        with open(self.table_file_location, 'r') as fin:
            tables = [dict(i) for i in csv.DictReader(fin)]

        results = []
        for table_dict in tables:
            db = table_dict['database']
            cluster = table_dict['cluster']
            schema = table_dict['schema']
            table = table_dict['name']
            id = self._get_key(db, cluster, schema, table)
            columns = parsed_columns[id]
            if columns is None:
                columns = []
            table = TableMetadata(database=table_dict['database'],
                                  cluster=table_dict['cluster'],
                                  schema=table_dict['schema'],
                                  name=table_dict['name'],
                                  description=table_dict['description'],
                                  columns=columns,
                                  is_view=table_dict['is_view'],
                                  tags=table_dict['tags']
                                  )
            results.append(table)
        self._iter = iter(results)

    def extract(self):
        # type: () -> Any
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self):
        # type: () -> str
        return 'extractor.csvtablecolumn'


def create_table_column_job(table_path, column_path):
    tmp_folder = '/var/tmp/amundsen/table_column'
    node_files_folder = '{tmp_folder}/nodes'.format(tmp_folder=tmp_folder)
    relationship_files_folder = '{tmp_folder}/relationships'.format(tmp_folder=tmp_folder)
    extractor = CSVTableColumnExtractor()
    csv_loader = FsNeo4jCSVLoader()
    task = DefaultTask(extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())
    job_config = ConfigFactory.from_dict({
        'extractor.csvtablecolumn.{}'.format(CSVTableColumnExtractor.TABLE_FILE_LOCATION): table_path,
        'extractor.csvtablecolumn.{}'.format(CSVTableColumnExtractor.COLUMN_FILE_LOCATION): column_path,
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


if __name__ == "__main__":
    # Uncomment next line to get INFO level logging
    # logging.basicConfig(level=logging.INFO)

    load_table_data_from_csv('sample_table_programmatic_source.csv', 'programmatic')
    load_table_column_stats_from_csv('sample_table_column_stats.csv')
    load_watermark_data_from_csv('sample_watermark.csv')
    load_table_owner_data_from_csv('sample_table_owner.csv')
    load_usage_data_from_csv('sample_column_usage.csv')
    load_user_data_from_csv('sample_user.csv')
    load_application_data_from_csv('sample_application.csv')
    load_source_data_from_csv('sample_source.csv')
    load_tag_data_from_csv('sample_tags.csv')
    load_test_last_updated_data_from_csv('sample_table_last_updated.csv')

    if create_connection(DB_FILE):

        # start table and column job
        table_path = 'example/sample_data/sample_table.csv'
        col_path = 'example/sample_data/sample_col.csv'
        # start table and column job
        table_and_col_job = create_table_column_job(
            table_path,
            col_path
        )
        table_and_col_job.launch()

        # start programmatic table job
        job2 = create_sample_job('programmatic',
                                 'databuilder.models.table_metadata.TableMetadata')
        job2.launch()

        # start table stats job
        job_table_stats = create_sample_job('test_table_column_stats',
                                            'databuilder.models.table_stats.TableColumnStats')
        job_table_stats.launch()

        # # start watermark job
        job3 = create_sample_job('test_watermark_metadata',
                                 'databuilder.models.watermark.Watermark')
        job3.launch()

        # start owner job
        job_table_owner = create_sample_job('test_table_owner_metadata',
                                            'databuilder.models.table_owner.TableOwner')
        job_table_owner.launch()

        # start usage job
        job_col_usage = create_sample_job('test_usage_metadata',
                                          'databuilder.models.column_usage_model.ColumnUsageModel')
        job_col_usage.launch()

        # start user job
        job_user = create_sample_job('test_user_metadata',
                                     'databuilder.models.user.User')
        job_user.launch()

        # start application job
        job_app = create_sample_job('test_application_metadata',
                                    'databuilder.models.application.Application')
        job_app.launch()

        # start job_source job
        job_source = create_sample_job('test_source_metadata',
                                       'databuilder.models.table_source.TableSource')
        job_source.launch()

        job_tag = create_sample_job('test_tag_metadata',
                                    'databuilder.models.table_metadata.TagMetadata')
        job_tag.launch()

        # start job_source job
        job_table_last_updated = create_sample_job('test_table_last_updated_metadata',
                                                   'databuilder.models.table_last_updated.TableLastUpdated')
        job_table_last_updated.launch()

        # start last updated job
        job_lastupdated = create_last_updated_job()
        job_lastupdated.launch()

        # start Elasticsearch publish jobs
        job_es_table = create_es_publisher_sample_job(
            elasticsearch_index_alias='table_search_index',
            elasticsearch_doc_type_key='table',
            model_name='databuilder.models.table_elasticsearch_document.TableESDocument')
        job_es_table.launch()

        user_cypher_query = textwrap.dedent(
            """
            MATCH (user:User)
            OPTIONAL MATCH (user)-[read:READ]->(a)
            OPTIONAL MATCH (user)-[own:OWNER_OF]->(b)
            OPTIONAL MATCH (user)-[follow:FOLLOWED_BY]->(c)
            OPTIONAL MATCH (user)-[manage_by:MANAGE_BY]->(manager)
            with user, a, b, c, read, own, follow, manager
            where user.full_name is not null
            return user.email as email, user.first_name as first_name, user.last_name as last_name,
            user.full_name as full_name, user.github_username as github_username, user.team_name as team_name,
            user.employee_type as employee_type, manager.email as manager_email, user.slack_id as slack_id,
            user.is_active as is_active,
            REDUCE(sum_r = 0, r in COLLECT(DISTINCT read)| sum_r + r.read_count) AS total_read,
            count(distinct b) as total_own,
            count(distinct c) AS total_follow
            order by user.email
            """
        )

        user_elasticsearch_mapping = """
            {
              "mappings":{
                "user":{
                  "properties": {
                    "email": {
                      "type":"text",
                      "analyzer": "simple",
                      "fields": {
                        "raw": {
                          "type": "keyword"
                        }
                      }
                    },
                    "first_name": {
                      "type":"text",
                      "analyzer": "simple",
                      "fields": {
                        "raw": {
                          "type": "keyword"
                        }
                      }
                    },
                    "last_name": {
                      "type":"text",
                      "analyzer": "simple",
                      "fields": {
                        "raw": {
                          "type": "keyword"
                        }
                      }
                    },
                    "full_name": {
                      "type":"text",
                      "analyzer": "simple",
                      "fields": {
                        "raw": {
                          "type": "keyword"
                        }
                      }
                    },
                    "total_read":{
                      "type": "long"
                    },
                    "total_own": {
                      "type": "long"
                    },
                    "total_follow": {
                      "type": "long"
                    }
                  }
                }
              }
            }
        """

        job_es_user = create_es_publisher_sample_job(
            elasticsearch_index_alias='user_search_index',
            elasticsearch_doc_type_key='user',
            model_name='databuilder.models.user_elasticsearch_document.UserESDocument',
            cypher_query=user_cypher_query,
            elasticsearch_mapping=user_elasticsearch_mapping)
        job_es_user.launch()
