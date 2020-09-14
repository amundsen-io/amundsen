# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from pathlib import Path
import uuid

from elasticsearch import Elasticsearch
from pyhocon import ConfigFactory

from databuilder.extractor.glue_extractor import GlueExtractor
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.extractor.neo4j_search_data_extractor import Neo4jSearchDataExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.publisher.elasticsearch_publisher import ElasticsearchPublisher
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from databuilder.task.task import DefaultTask
from databuilder.transformer.base_transformer import NoopTransformer


# change the following values to your liking
NEO4J_ENDPOINT = 'bolt://127.0.0.1:7687'
NEO4j_USERNAME = 'neo4j'
NEO4j_PASSWORD = 'test'
GLUE_CLUSTER_KEY = 'test_cluster_key'

es = Elasticsearch([{'host': '127.0.0.1'}, ])


def create_glue_extractor_job():

    tmp_folder = '/var/tmp/amundsen/table_metadata'
    node_files_folder = Path(tmp_folder, 'nodes')
    relationship_files_folder = Path(tmp_folder, 'relationships')

    job_config = ConfigFactory.from_dict({
        'extractor.glue.{}'.format(GlueExtractor.CLUSTER_KEY):
            GLUE_CLUSTER_KEY,
        'extractor.glue.{}'.format(GlueExtractor.FILTER_KEY):
            [],
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH):
            node_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH):
            relationship_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NODE_FILES_DIR):
            node_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.RELATION_FILES_DIR):
            relationship_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_END_POINT_KEY):
            NEO4J_ENDPOINT,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_USER):
            NEO4j_USERNAME,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_PASSWORD):
            NEO4j_PASSWORD,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.JOB_PUBLISH_TAG):
            str(int(datetime.utcnow().timestamp()))
    })

    return DefaultJob(conf=job_config,
                      task=DefaultTask(
                          extractor=GlueExtractor(),
                          loader=FsNeo4jCSVLoader(),
                          transformer=NoopTransformer()),
                      publisher=Neo4jCsvPublisher())


def create_es_publisher_job():

    # loader saves data to this location and publisher reads it from here
    extracted_search_data_path = '/var/tmp/amundsen/search_data.json'

    task = DefaultTask(loader=FSElasticsearchJSONLoader(),
                       extractor=Neo4jSearchDataExtractor(),
                       transformer=NoopTransformer())

    elasticsearch_client = es
    # unique name of new index in Elasticsearch
    elasticsearch_new_index_key = 'tables' + str(uuid.uuid4())
    # related to mapping type from /databuilder/publisher/elasticsearch_publisher.py#L38
    elasticsearch_new_index_key_type = 'table'
    # alias for Elasticsearch used in amundsensearchlibrary/search_service/config.py as an index
    elasticsearch_index_alias = 'table_search_index'

    job_config = ConfigFactory.from_dict({
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.GRAPH_URL_CONFIG_KEY):
            NEO4J_ENDPOINT,
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY):
            'databuilder.models.table_elasticsearch_document.TableESDocument',
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_USER):
            NEO4j_USERNAME,
        'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_PW):
            NEO4j_PASSWORD,
        'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_PATH_CONFIG_KEY):
            extracted_search_data_path,
        'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_MODE_CONFIG_KEY):
            'w',
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_PATH_CONFIG_KEY):
            extracted_search_data_path,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_MODE_CONFIG_KEY):
            'r',
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_CLIENT_CONFIG_KEY):
            elasticsearch_client,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY):
            elasticsearch_new_index_key,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_DOC_TYPE_CONFIG_KEY):
            elasticsearch_new_index_key_type,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_ALIAS_CONFIG_KEY):
            elasticsearch_index_alias
    })

    return DefaultJob(conf=job_config,
                      task=task,
                      publisher=ElasticsearchPublisher())


if __name__ == "__main__":

    glue_job = create_glue_extractor_job()
    glue_job.launch()

    es_job = create_es_publisher_job()
    es_job.launch()
