# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from cProfile import run
import uuid
from datetime import datetime
from pathlib import Path

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
from databuilder.extractor.csv_extractor import (
    CsvColumnLineageExtractor, CsvExtractor, CsvTableBadgeExtractor, CsvTableColumnExtractor, CsvTableLineageExtractor,
)

# change the following values to your liking
NEO4J_ENDPOINT = 'bolt://127.0.0.1:7687'
NEO4j_USERNAME = 'admin'
NEO4j_PASSWORD = 'admin'
GLUE_CLUSTER_KEY = 'MGL' 

es = Elasticsearch([{'host': '127.0.0.1'}, ])


def create_glue_extractor_job():
    tmp_folder = '/var/tmp/amundsen/table_metadata'
    node_files_folder = Path(tmp_folder, 'nodes')
    relationship_files_folder = Path(tmp_folder, 'relationships')

    job_config = ConfigFactory.from_dict({
        f'extractor.glue.{GlueExtractor.CLUSTER_KEY}': GLUE_CLUSTER_KEY,
        f'extractor.glue.{GlueExtractor.FILTER_KEY}': [
            
                            
                {
                    "Key": "DatabaseName",
                    "Value": "mgl"
                },
                {
                    "Key": "Name",
                    "Value": "tb_tab_accentiv_fatitens"
                    "key": "Owners"
                    "Value" : ['kelvin.sousa@iob.com.br', 'joao.matos@iob.com.br']
                },
                


            ],
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': node_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NODE_FILES_DIR}': node_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.RELATION_FILES_DIR}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_END_POINT_KEY}': NEO4J_ENDPOINT,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_USER}': NEO4j_USERNAME,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_PASSWORD}': NEO4j_PASSWORD,
        f'publisher.neo4j.{neo4j_csv_publisher.JOB_PUBLISH_TAG}': str(int(datetime.utcnow().timestamp()))
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
        f'extractor.search_data.extractor.neo4j.{Neo4jExtractor.GRAPH_URL_CONFIG_KEY}':
            NEO4J_ENDPOINT,
        f'extractor.search_data.extractor.neo4j.{Neo4jExtractor.MODEL_CLASS_CONFIG_KEY}':
            'databuilder.models.table_elasticsearch_document.TableESDocument',
        f'extractor.search_data.extractor.neo4j.{Neo4jExtractor.NEO4J_AUTH_USER}':
            NEO4j_USERNAME,
        f'extractor.search_data.extractor.neo4j.{Neo4jExtractor.NEO4J_AUTH_PW}':
            NEO4j_PASSWORD,
        f'loader.filesystem.elasticsearch.{FSElasticsearchJSONLoader.FILE_PATH_CONFIG_KEY}':
            extracted_search_data_path,
        f'loader.filesystem.elasticsearch.{FSElasticsearchJSONLoader.FILE_MODE_CONFIG_KEY}':
            'w',
        f'publisher.elasticsearch.{ElasticsearchPublisher.FILE_PATH_CONFIG_KEY}':
            extracted_search_data_path,
        f'publisher.elasticsearch.{ElasticsearchPublisher.FILE_MODE_CONFIG_KEY}':
            'r',
        f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_CLIENT_CONFIG_KEY}':
            elasticsearch_client,
        f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY}':
            elasticsearch_new_index_key,
        f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_DOC_TYPE_CONFIG_KEY}':
            elasticsearch_new_index_key_type,
        f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_ALIAS_CONFIG_KEY}':
            elasticsearch_index_alias
    })

    return DefaultJob(conf=job_config,
                      task=task,
                      publisher=ElasticsearchPublisher())

def run_csv_job(file_loc, job_name, model):
    tmp_folder = f'/var/tmp/amundsen/{job_name}'
    node_files_folder = f'{tmp_folder}/nodes'
    relationship_files_folder = f'{tmp_folder}/relationships'

    csv_extractor = CsvExtractor()
    csv_loader = FsNeo4jCSVLoader()

    task = DefaultTask(extractor=csv_extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())

    job_config = ConfigFactory.from_dict({
        'extractor.csv.file_location': file_loc,
        'extractor.csv.model_class': model,
        'loader.filesystem_csv_neo4j.node_dir_path': node_files_folder,
        'loader.filesystem_csv_neo4j.relationship_dir_path': relationship_files_folder,
        'loader.filesystem_csv_neo4j.delete_created_directories': True,
        'publisher.neo4j.node_files_directory': node_files_folder,
        'publisher.neo4j.relation_files_directory': relationship_files_folder,
        'publisher.neo4j.neo4j_endpoint': NEO4J_ENDPOINT,
        'publisher.neo4j.neo4j_user': NEO4j_USERNAME,
        'publisher.neo4j.neo4j_password': NEO4j_PASSWORD,
        'publisher.neo4j.neo4j_encrypted': False,
        'publisher.neo4j.job_publish_tag': 'unique_tag',  # should use unique tag here like {ds}
    })

    DefaultJob(conf=job_config,
               task=task,
               publisher=Neo4jCsvPublisher()).launch()

if __name__ == "__main__":
    glue_job = create_glue_extractor_job()
    glue_job.launch()

    es_job = create_es_publisher_job()
    es_job.launch()
    run_csv_job('databuilder/example/sample_data/sample_table_owner.csv', 'test_table_owner_metadata',
                'databuilder.models.table_owner.TableOwner')