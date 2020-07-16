# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

"""
This is a example script which demo how to load data into neo4j without using Airflow DAG.
"""

import logging
import os
from pyhocon import ConfigFactory

import sys
import uuid

from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.extractor.db2_metadata_extractor import Db2MetadataExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from databuilder.task.task import DefaultTask

from elasticsearch import Elasticsearch
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.extractor.neo4j_search_data_extractor import Neo4jSearchDataExtractor
from databuilder.transformer.base_transformer import NoopTransformer
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.publisher.elasticsearch_publisher import ElasticsearchPublisher

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
# Disable Db2 logging
logging.getLogger("db2.connector.network").disabled = True

DB2_CONN_STRING = 'db2+ibm_db://username:password@database.host.name:50000/DB;'

# set env NEO4J_HOST to override localhost
NEO4J_ENDPOINT = 'bolt://{}:7687'.format(os.getenv('NEO4J_HOST', 'localhost'))
neo4j_endpoint = NEO4J_ENDPOINT

neo4j_user = 'neo4j'
neo4j_password = 'test'

es_host = None
neo_host = None
if len(sys.argv) > 1:
    es_host = sys.argv[1]
if len(sys.argv) > 2:
    neo_host = sys.argv[2]

es = Elasticsearch([
    {'host': es_host if es_host else 'localhost'},
])

IGNORED_SCHEMAS = ['\'SYSIBM\'', '\'SYSIBMTS\'', '\'SYSTOOLS\'', '\'SYSCAT\'', '\'SYSIBMADM\'', '\'SYSSTAT\'']


def create_sample_db2_job():

    where_clause = "WHERE c.TABSCHEMA not in ({0}) ;".format(','.join(IGNORED_SCHEMAS))

    tmp_folder = '/var/tmp/amundsen/{}'.format('tables')
    node_files_folder = '{tmp_folder}/nodes'.format(tmp_folder=tmp_folder)
    relationship_files_folder = '{tmp_folder}/relationships'.format(tmp_folder=tmp_folder)

    sql_extractor = Db2MetadataExtractor()
    csv_loader = FsNeo4jCSVLoader()

    task = DefaultTask(extractor=sql_extractor,
                       loader=csv_loader)

    job_config = ConfigFactory.from_dict({
        'extractor.db2_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): DB2_CONN_STRING,
        'extractor.db2_metadata.{}'.format(Db2MetadataExtractor.DATABASE_KEY): 'DEMODB',
        'extractor.db2_metadata.{}'.format(Db2MetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY): where_clause,
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
    extracted_search_data_path = '/var/tmp/amundsen/db2_data.json'

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


if __name__ == "__main__":
    job = create_sample_db2_job()
    job.launch()

    job_es_table = create_es_publisher_sample_job(
        elasticsearch_index_alias='table_search_index',
        elasticsearch_doc_type_key='table',
        model_name='databuilder.models.table_elasticsearch_document.TableESDocument')
    job_es_table.launch()
