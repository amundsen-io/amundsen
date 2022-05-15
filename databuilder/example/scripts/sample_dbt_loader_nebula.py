# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

"""
This is a example script demonstrating how to load data into Neo4j and
Elasticsearch without using an Airflow DAG.
It contains several jobs:
- `run_csv_job`: runs a job that extracts table data from a CSV, loads (writes)
  this into a different local directory as a csv, then publishes this data to
  Nebula Graph.
- `run_table_column_job`: does the same thing as `run_csv_job`, but with a csv
  containing column data.
- `create_last_updated_job`: creates a job that gets the current time, dumps it
  into a predefined model schema, and publishes this to Nebula Graph.
- `create_es_publisher_sample_job`: creates a job that extracts data from Nebula Graph
  and pubishes it into elasticsearch.
For other available extractors, please take a look at
https://github.com/amundsen-io/amundsendatabuilder#list-of-extractors
"""

import json
import logging
import os
import sys
import uuid

from elasticsearch import Elasticsearch
from pyhocon import ConfigFactory
from sqlalchemy.ext.declarative import declarative_base

from databuilder.extractor.dbt_extractor import DbtExtractor
from databuilder.extractor.nebula_search_data_extractor import NebulaSearchDataExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.loader.file_system_nebula_csv_loader import FsNebulaCSVLoader
from databuilder.publisher.elasticsearch_publisher import ElasticsearchPublisher
from databuilder.publisher.nebula_csv_publisher import NebulaCsvPublisher
from databuilder.task.task import DefaultTask
from databuilder.task.search.search_metadata_to_elasticsearch_task import SearchMetadatatoElasticasearchTask
from databuilder.transformer.base_transformer import NoopTransformer

es_host = os.getenv('CREDENTIALS_ELASTICSEARCH_PROXY_HOST', 'localhost')
es_port = os.getenv('CREDENTIALS_ELASTICSEARCH_PROXY_PORT', 9200)
nebula_endpoints = os.getenv('CREDENTIALS_NEBULA_ENDPOINTS', 'localhost:9669')
nebula_space = os.getenv('NEBULA_SPACE', 'amundsen')

if len(sys.argv) > 1:
    es_host = sys.argv[1]
if len(sys.argv) > 2:
    nebula_endpoints = sys.argv[2]

es = Elasticsearch([
    {'host': es_host if es_host else 'localhost'},
])

Base = declarative_base()

nebula_user = 'root'
nebula_password = 'nebula'

LOGGER = logging.getLogger(__name__)


def run_dbt_job(database_name, catalog_file_loc, manifest_file_loc, source_url=None):
    tmp_folder = '/var/tmp/amundsen/table_metadata'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'

    dbt_extractor = DbtExtractor()
    csv_loader = FsNebulaCSVLoader()

    task = DefaultTask(extractor=dbt_extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())

    # Catalop and manifest files can be passed in as file locations or a valid python
    # dict, allowing you to retrieve the files from S3 or another source and pass it in
    with open(manifest_file_loc, 'rb') as f:
        manifest_data = json.load(f)

    job_config = ConfigFactory.from_dict({
        'extractor.dbt.database_name': database_name,
        'extractor.dbt.catalog_json': catalog_file_loc,  # File
        'extractor.dbt.manifest_json': json.dumps(manifest_data),  # JSON Dumped objecy
        'extractor.dbt.source_url': source_url,
        'loader.filesystem_csv_nebula.vertex_dir_path': vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path': edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories': True,
        'publisher.nebula.vertex_files_directory': vertex_files_folder,
        'publisher.nebula.edge_files_directory': edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints': nebula_endpoints,
        'publisher.nebula.nebula_user': nebula_user,
        'publisher.nebula.nebula_password': nebula_password,
        'publisher.nebula.job_publish_tag': 'unique_tag',  # should use unique tag here like {ds}
    })

    DefaultJob(conf=job_config,
               task=task,
               publisher=NebulaCsvPublisher()).launch()


def create_es_publisher_sample_job(elasticsearch_index_alias='table_search_index',
                                   elasticsearch_doc_type_key='table',
                                   model_name='databuilder.models.table_elasticsearch_document.TableESDocument',
                                   entity_type='table',
                                   elasticsearch_mapping=None):
    """
    :param elasticsearch_index_alias:  alias for Elasticsearch used in
                                       amundsensearchlibrary/search_service/config.py as an index
    :param elasticsearch_doc_type_key: name the ElasticSearch index is prepended with. Defaults to `table` resulting in
                                       `table_{uuid}`
    :param model_name:                 the Databuilder model class used in transporting between Extractor and Loader
    :param entity_type:                Entity type handed to the `NebulaSearchDataExtractor` class, used to determine
                                       Cypher query to extract data from Neo4j. Defaults to `table`.
    :param elasticsearch_mapping:      Elasticsearch field mapping "DDL" handed to the `ElasticsearchPublisher` class,
                                       if None is given (default) it uses the `Table` query baked into the Publisher
    """
    # loader saves data to this location and publisher reads it from here
    extracted_search_data_path = '/var/tmp/amundsen/search_data.json'

    task = DefaultTask(loader=FSElasticsearchJSONLoader(),
                       extractor=NebulaSearchDataExtractor(),
                       transformer=NoopTransformer())

    # elastic search client instance
    elasticsearch_client = es
    # unique name of new index in Elasticsearch
    elasticsearch_new_index_key = f'{elasticsearch_doc_type_key}_{uuid.uuid4()}'

    job_config = ConfigFactory.from_dict({
        'extractor.search_data.entity_type': entity_type,
        'extractor.search_data.extractor.nebula.nebula_endpoints': nebula_endpoints,
        'extractor.search_data.extractor.nebula.model_class': model_name,
        'extractor.search_data.extractor.nebula.nebula_auth_user': nebula_user,
        'extractor.search_data.extractor.nebula.nebula_auth_pw': nebula_password,
        'extractor.search_data.extractor.nebula.nebula_space': nebula_space,
        'loader.filesystem.elasticsearch.file_path': extracted_search_data_path,
        'loader.filesystem.elasticsearch.mode': 'w',
        'publisher.elasticsearch.file_path': extracted_search_data_path,
        'publisher.elasticsearch.mode': 'r',
        'publisher.elasticsearch.client': elasticsearch_client,
        'publisher.elasticsearch.new_index': elasticsearch_new_index_key,
        'publisher.elasticsearch.doc_type': elasticsearch_doc_type_key,
        'publisher.elasticsearch.alias': elasticsearch_index_alias,
    })

    # only optionally add these keys, so need to dynamically `put` them
    if elasticsearch_mapping:
        job_config.put(f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_MAPPING_CONFIG_KEY}',
                       elasticsearch_mapping)

    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=ElasticsearchPublisher())
    return job

def run_search_metadata_task(resource_type: str):
    task_config = {
        f'task.search_metadata_to_elasticsearch.{SearchMetadatatoElasticasearchTask.ENTITY_TYPE}': resource_type,
        f'task.search_metadata_to_elasticsearch.{SearchMetadatatoElasticasearchTask.ELASTICSEARCH_CLIENT_CONFIG_KEY}': es,
        f'task.search_metadata_to_elasticsearch.{SearchMetadatatoElasticasearchTask.ELASTICSEARCH_ALIAS_CONFIG_KEY}': f'{resource_type}_search_index',
        'extractor.search_data.entity_type': resource_type,
        'extractor.search_data.extractor.nebula.nebula_endpoints': nebula_endpoints,
        'extractor.search_data.extractor.nebula.nebula_auth_user': nebula_user,
        'extractor.search_data.extractor.nebula.nebula_auth_pw': nebula_password,
        'extractor.search_data.extractor.nebula.nebula_space': nebula_space,
    }

    job_config = ConfigFactory.from_dict({
        **task_config,
    })

    extractor = NebulaSearchDataExtractor()
    task = SearchMetadatatoElasticasearchTask(extractor=extractor)

    job = DefaultJob(conf=job_config, task=task)

    job.launch()

if __name__ == "__main__":
    # Uncomment next line to get INFO level logging
    logging.basicConfig(level=logging.INFO)

    run_dbt_job(
        database_name='snowflake',
        catalog_file_loc='example/sample_data/dbt/catalog.json',
        manifest_file_loc='example/sample_data/dbt/manifest.json',
        source_url='https://github.com/your-company/your-repo/tree/main'
    )

    # with ElasticsearchPublisher, which will be deprecated
    job_es_table = create_es_publisher_sample_job(
        elasticsearch_index_alias='table_search_index',
        elasticsearch_doc_type_key='table',
        entity_type='table',
        model_name='databuilder.models.table_elasticsearch_document.TableESDocument')
    job_es_table.launch()

    # with SearchMetadatatoElasticasearchTask
    run_search_metadata_task('table')