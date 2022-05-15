# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
"""
This is a example script demonstrating how to load data into Nebula and
Elasticsearch without using an Airflow DAG.

It contains several jobs:
- `run_csv_job`: runs a job that extracts table data from a CSV, loads (writes)
  this into a different local directory as a csv, then publishes this data to
  nebula.
- `run_table_column_job`: does the same thing as `run_csv_job`, but with a csv
  containing column data.
- `create_last_updated_job`: creates a job that gets the current time, dumps it
  into a predefined model schema, and publishes this to nebula.
- `create_es_publisher_sample_job`: creates a job that extracts data from nebula
  and pubishes it into elasticsearch.

For other available extractors, please take a look at
https://github.com/amundsen-io/amundsendatabuilder#list-of-extractors
"""

import logging
import os
import sys
import uuid

from amundsen_common.models.index_map import DASHBOARD_ELASTICSEARCH_INDEX_MAPPING, USER_INDEX_MAP
from distutils.util import strtobool
from elasticsearch import Elasticsearch
from pyhocon import ConfigFactory
from sqlalchemy.ext.declarative import declarative_base

from databuilder.extractor.csv_extractor import (
    CsvColumnLineageExtractor, CsvExtractor, CsvTableBadgeExtractor,
    CsvTableColumnExtractor, CsvTableLineageExtractor, CsvTableQueryExtractor,
    CsvTableQueryJoinExtractor, CsvTableQueryWhereExtractor,
    CsvTableQueryExecutionExtractor)
from databuilder.extractor.es_last_updated_extractor import EsLastUpdatedExtractor
from databuilder.extractor.nebula_search_data_extractor import NebulaSearchDataExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.loader.file_system_nebula_csv_loader import FsNebulaCSVLoader
from databuilder.publisher.elasticsearch_publisher import ElasticsearchPublisher
from databuilder.publisher.nebula_csv_publisher import NebulaCsvPublisher
from databuilder.task.task import DefaultTask
from databuilder.task.search.search_metadata_to_elasticsearch_task import SearchMetadatatoElasticasearchTask
from databuilder.transformer.base_transformer import ChainedTransformer, NoopTransformer
from databuilder.transformer.complex_type_transformer import PARSING_FUNCTION, ComplexTypeTransformer
from databuilder.transformer.dict_to_model import MODEL_CLASS, DictToModel
from databuilder.transformer.generic_transformer import (
    CALLBACK_FUNCTION,
    FIELD_NAME,
    GenericTransformer,
)

es_host = os.getenv('CREDENTIALS_ELASTICSEARCH_PROXY_HOST', 'localhost')
NEBULA_ENDPOINTS = os.getenv('CREDENTIALS_NEBULA_ENDPOINTS', 'localhost:9669')
nebula_space = os.getenv('NEBULA_SPACE', 'amundsen')
es_port = os.getenv('CREDENTIALS_ELASTICSEARCH_PROXY_PORT', 9200)

if len(sys.argv) > 1:
    es_host = sys.argv[1]
if len(sys.argv) > 2:
    nebula_endpoints = sys.argv[2]

es = Elasticsearch([
    {
        'host': es_host,
        'port': es_port
    },
])

Base = declarative_base()

nebula_endpoints = NEBULA_ENDPOINTS

nebula_user = 'root'
nebula_password = 'nebula'

LOGGER = logging.getLogger(__name__)


def run_csv_job(file_loc, job_name, model):
    tmp_folder = f'/var/tmp/amundsen/{job_name}'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'

    csv_extractor = CsvExtractor()
    csv_loader = FsNebulaCSVLoader()

    task = DefaultTask(extractor=csv_extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())

    job_config = ConfigFactory.from_dict({
        'extractor.csv.file_location':
        file_loc,
        'extractor.csv.model_class':
        model,
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories':
        True,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })

    DefaultJob(conf=job_config, task=task,
               publisher=NebulaCsvPublisher()).launch()


def run_table_badge_job(table_path, badge_path):
    tmp_folder = '/var/tmp/amundsen/table_badge'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'
    extractor = CsvTableBadgeExtractor()
    csv_loader = FsNebulaCSVLoader()
    task = DefaultTask(extractor=extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())
    job_config = ConfigFactory.from_dict({
        'extractor.csvtablebadge.table_file_location':
        table_path,
        'extractor.csvtablebadge.badge_file_location':
        badge_path,
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories':
        True,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=NebulaCsvPublisher())
    job.launch()


def run_table_column_job(table_path, column_path):
    tmp_folder = '/var/tmp/amundsen/table_column'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'
    extractor = CsvTableColumnExtractor()
    csv_loader = FsNebulaCSVLoader()
    task = DefaultTask(extractor,
                       loader=csv_loader,
                       transformer=ComplexTypeTransformer())

    job_config = ConfigFactory.from_dict({
        f'transformer.complex_type.{PARSING_FUNCTION}':
        'databuilder.utils.hive_complex_type_parser.parse_hive_type',
        'extractor.csvtablecolumn.table_file_location':
        table_path,
        'extractor.csvtablecolumn.column_file_location':
        column_path,
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories':
        True,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=NebulaCsvPublisher())
    job.launch()


def run_table_lineage_job(table_lineage_path):
    tmp_folder = '/var/tmp/amundsen/table_column'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'
    extractor = CsvTableLineageExtractor()
    csv_loader = FsNebulaCSVLoader()
    task = DefaultTask(extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())
    job_config = ConfigFactory.from_dict({
        'extractor.csvtablelineage.table_lineage_file_location':
        table_lineage_path,
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories':
        True,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=NebulaCsvPublisher())
    job.launch()


def run_column_lineage_job(column_lineage_path):
    tmp_folder = '/var/tmp/amundsen/table_column'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'
    extractor = CsvColumnLineageExtractor()
    csv_loader = FsNebulaCSVLoader()
    task = DefaultTask(extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())
    job_config = ConfigFactory.from_dict({
        'extractor.csvcolumnlineage.column_lineage_file_location':
        column_lineage_path,
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories':
        True,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=NebulaCsvPublisher())
    job.launch()


def run_table_query_job(user_path, column_path, table_path, query_path):
    tmp_folder = '/var/tmp/amundsen/table_query'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'
    extractor = CsvTableQueryExtractor()
    csv_loader = FsNebulaCSVLoader()
    task = DefaultTask(extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())
    job_config = ConfigFactory.from_dict({
        'extractor.csvtablequery.user_file_location':
        user_path,
        'extractor.csvtablequery.column_file_location':
        column_path,
        'extractor.csvtablequery.table_file_location':
        table_path,
        'extractor.csvtablequery.query_file_location':
        query_path,
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories':
        True,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=NebulaCsvPublisher())
    job.launch()


def run_table_join_job(user_path, column_path, table_path, query_path,
                       join_path):
    tmp_folder = '/var/tmp/amundsen/table_join'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'
    extractor = CsvTableQueryJoinExtractor()
    csv_loader = FsNebulaCSVLoader()
    task = DefaultTask(extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())
    job_config = ConfigFactory.from_dict({
        'extractor.csvtablequeryjoin.user_file_location':
        user_path,
        'extractor.csvtablequeryjoin.column_file_location':
        column_path,
        'extractor.csvtablequeryjoin.table_file_location':
        table_path,
        'extractor.csvtablequeryjoin.query_file_location':
        query_path,
        'extractor.csvtablequeryjoin.join_file_location':
        join_path,
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories':
        True,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=NebulaCsvPublisher())
    job.launch()


def run_table_where_job(user_path, column_path, table_path, query_path,
                        where_path):
    tmp_folder = '/var/tmp/amundsen/table_where'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'
    extractor = CsvTableQueryWhereExtractor()
    csv_loader = FsNebulaCSVLoader()
    task = DefaultTask(extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())
    job_config = ConfigFactory.from_dict({
        'extractor.csvtablequerywhere.user_file_location':
        user_path,
        'extractor.csvtablequerywhere.column_file_location':
        column_path,
        'extractor.csvtablequerywhere.table_file_location':
        table_path,
        'extractor.csvtablequerywhere.query_file_location':
        query_path,
        'extractor.csvtablequerywhere.where_file_location':
        where_path,
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories':
        True,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=NebulaCsvPublisher())
    job.launch()


def run_table_execution_job(user_path, column_path, table_path, query_path,
                            execution_path):
    tmp_folder = '/var/tmp/amundsen/table_execution'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'
    extractor = CsvTableQueryExecutionExtractor()
    csv_loader = FsNebulaCSVLoader()
    task = DefaultTask(extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())
    job_config = ConfigFactory.from_dict({
        'extractor.csvtablequeryexecution.user_file_location':
        user_path,
        'extractor.csvtablequeryexecution.column_file_location':
        column_path,
        'extractor.csvtablequeryexecution.table_file_location':
        table_path,
        'extractor.csvtablequeryexecution.query_file_location':
        query_path,
        'extractor.csvtablequeryexecution.execution_file_location':
        execution_path,
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'loader.filesystem_csv_nebula.delete_created_directories':
        True,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=NebulaCsvPublisher())
    job.launch()


def create_last_updated_job():
    # loader saves data to these folders and publisher reads it from here
    tmp_folder = '/var/tmp/amundsen/last_updated_data'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'

    task = DefaultTask(extractor=EsLastUpdatedExtractor(),
                       loader=FsNebulaCSVLoader())

    job_config = ConfigFactory.from_dict({
        'extractor.es_last_updated.model_class':
        'databuilder.models.es_last_updated.ESLastUpdated',
        'loader.filesystem_csv_nebula.vertex_dir_path':
        vertex_files_folder,
        'loader.filesystem_csv_nebula.edge_dir_path':
        edge_dir_files_folder,
        'publisher.nebula.vertex_files_directory':
        vertex_files_folder,
        'publisher.nebula.edge_files_directory':
        edge_dir_files_folder,
        'publisher.nebula.nebula_endpoints':
        nebula_endpoints,
        'publisher.nebula.nebula_user':
        nebula_user,
        'publisher.nebula.nebula_password':
        nebula_password,
        'publisher.nebula.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })

    return DefaultJob(conf=job_config,
                      task=task,
                      publisher=NebulaCsvPublisher())


def _str_to_list(str_val):
    return str_val.split(',')


def _str_to_bool(str_val):
    return bool(strtobool(str_val))


def create_application_job():
    # loader saves data to these folders and publisher reads it from here
    tmp_folder = '/var/tmp/amundsen/application'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'

    csv_extractor = CsvExtractor()
    csv_loader = FsNebulaCSVLoader()

    generic_transformer = GenericTransformer()
    dict_to_model_transformer = DictToModel()
    transformer = ChainedTransformer(
        transformers=[generic_transformer, dict_to_model_transformer],
        is_init_transformers=True)

    task = DefaultTask(extractor=csv_extractor,
                       loader=csv_loader,
                       transformer=transformer)
    publisher = NebulaCsvPublisher()

    job_config = ConfigFactory.from_dict({
        f'{csv_extractor.get_scope()}.file_location':
        'example/sample_data/sample_application.csv',
        f'{transformer.get_scope()}.{generic_transformer.get_scope()}.{FIELD_NAME}':
        'generates_table',
        f'{transformer.get_scope()}.{generic_transformer.get_scope()}.{CALLBACK_FUNCTION}':
        _str_to_bool,
        f'{transformer.get_scope()}.{dict_to_model_transformer.get_scope()}.{MODEL_CLASS}':
        'databuilder.models.application.Application',
        f'{csv_loader.get_scope()}.vertex_dir_path':
        vertex_files_folder,
        f'{csv_loader.get_scope()}.edge_dir_path':
        edge_dir_files_folder,
        f'{csv_loader.get_scope()}.delete_created_directories':
        True,
        f'{publisher.get_scope()}.vertex_files_directory':
        vertex_files_folder,
        f'{publisher.get_scope()}.edge_files_directory':
        edge_dir_files_folder,
        f'{publisher.get_scope()}.nebula_endpoints':
        nebula_endpoints,
        f'{publisher.get_scope()}.nebula_user':
        nebula_user,
        f'{publisher.get_scope()}.nebula_password':
        nebula_password,
        f'{publisher.get_scope()}.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })

    return DefaultJob(conf=job_config, task=task, publisher=publisher)


def create_dashboard_tables_job():
    # loader saves data to these folders and publisher reads it from here
    tmp_folder = '/var/tmp/amundsen/dashboard_table'
    vertex_files_folder = f'{tmp_folder}/nodes'
    edge_dir_files_folder = f'{tmp_folder}/relationships'

    csv_extractor = CsvExtractor()
    csv_loader = FsNebulaCSVLoader()

    generic_transformer = GenericTransformer()
    dict_to_model_transformer = DictToModel()
    transformer = ChainedTransformer(
        transformers=[generic_transformer, dict_to_model_transformer],
        is_init_transformers=True)

    task = DefaultTask(extractor=csv_extractor,
                       loader=csv_loader,
                       transformer=transformer)
    publisher = NebulaCsvPublisher()

    job_config = ConfigFactory.from_dict({
        f'{csv_extractor.get_scope()}.file_location':
        'example/sample_data/sample_dashboard_table.csv',
        f'{transformer.get_scope()}.{generic_transformer.get_scope()}.{FIELD_NAME}':
        'table_ids',
        f'{transformer.get_scope()}.{generic_transformer.get_scope()}.{CALLBACK_FUNCTION}':
        _str_to_list,
        f'{transformer.get_scope()}.{dict_to_model_transformer.get_scope()}.{MODEL_CLASS}':
        'databuilder.models.dashboard.dashboard_table.DashboardTable',
        f'{csv_loader.get_scope()}.vertex_dir_path':
        vertex_files_folder,
        f'{csv_loader.get_scope()}.edge_dir_path':
        edge_dir_files_folder,
        f'{csv_loader.get_scope()}.delete_created_directories':
        True,
        f'{publisher.get_scope()}.vertex_files_directory':
        vertex_files_folder,
        f'{publisher.get_scope()}.edge_files_directory':
        edge_dir_files_folder,
        f'{publisher.get_scope()}.nebula_endpoints':
        nebula_endpoints,
        f'{publisher.get_scope()}.nebula_user':
        nebula_user,
        f'{publisher.get_scope()}.nebula_password':
        nebula_password,
        f'{publisher.get_scope()}.job_publish_tag':
        'unique_tag',  # should use unique tag here like {ds}
    })

    return DefaultJob(conf=job_config, task=task, publisher=publisher)


def create_es_publisher_sample_job(
        elasticsearch_index_alias='table_search_index',
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
                                       query to extract data from Nebula. Defaults to `table`.
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
        'extractor.search_data.entity_type':
        entity_type,
        'extractor.search_data.extractor.nebula.nebula_endpoints':
        nebula_endpoints,
        'extractor.search_data.extractor.nebula.model_class':
        model_name,
        'extractor.search_data.extractor.nebula.nebula_auth_user':
        nebula_user,
        'extractor.search_data.extractor.nebula.nebula_auth_pw':
        nebula_password,
        'extractor.search_data.extractor.nebula.nebula_space':
        nebula_space,
        'loader.filesystem.elasticsearch.file_path':
        extracted_search_data_path,
        'loader.filesystem.elasticsearch.mode':
        'w',
        'publisher.elasticsearch.file_path':
        extracted_search_data_path,
        'publisher.elasticsearch.mode':
        'r',
        'publisher.elasticsearch.client':
        elasticsearch_client,
        'publisher.elasticsearch.new_index':
        elasticsearch_new_index_key,
        'publisher.elasticsearch.doc_type':
        elasticsearch_doc_type_key,
        'publisher.elasticsearch.alias':
        elasticsearch_index_alias,
    })

    # only optionally add these keys, so need to dynamically `put` them
    if elasticsearch_mapping:
        job_config.put(
            f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_MAPPING_CONFIG_KEY}',
            elasticsearch_mapping)

    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=ElasticsearchPublisher())
    return job


def run_search_metadata_task(resource_type: str):
    task_config = {
        f'task.search_metadata_to_elasticsearch.{SearchMetadatatoElasticasearchTask.ENTITY_TYPE}':
            resource_type,
        f'task.search_metadata_to_elasticsearch.{SearchMetadatatoElasticasearchTask.ELASTICSEARCH_CLIENT_CONFIG_KEY}':
            es,
        f'task.search_metadata_to_elasticsearch.{SearchMetadatatoElasticasearchTask.ELASTICSEARCH_ALIAS_CONFIG_KEY}':
            f'{resource_type}_search_index',
        'extractor.search_data.entity_type':
            resource_type,
        'extractor.search_data.extractor.nebula.nebula_endpoints':
            nebula_endpoints,
        'extractor.search_data.extractor.nebula.nebula_auth_user':
            nebula_user,
        'extractor.search_data.extractor.nebula.nebula_auth_pw':
            nebula_password,
        'extractor.search_data.extractor.nebula.nebula_space':
            nebula_space,
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
    logging.basicConfig(level=logging.DEBUG)

    run_table_column_job('example/sample_data/sample_table.csv',
                         'example/sample_data/sample_col.csv')
    run_table_badge_job('example/sample_data/sample_table.csv',
                        'example/sample_data/sample_badges.csv')
    run_table_lineage_job('example/sample_data/sample_table_lineage.csv')
    run_column_lineage_job('example/sample_data/sample_column_lineage.csv')
    run_csv_job('example/sample_data/sample_table_column_stats.csv',
                'test_table_column_stats',
                'databuilder.models.table_stats.TableColumnStats')
    run_csv_job('example/sample_data/sample_table_programmatic_source.csv',
                'test_programmatic_source',
                'databuilder.models.table_metadata.TableMetadata')
    run_csv_job('example/sample_data/sample_watermark.csv',
                'test_watermark_metadata',
                'databuilder.models.watermark.Watermark')
    run_csv_job('example/sample_data/sample_table_owner.csv',
                'test_table_owner_metadata',
                'databuilder.models.table_owner.TableOwner')
    run_csv_job('example/sample_data/sample_table_follower.csv',
                'test_table_follower_metadata',
                'databuilder.models.table_follower.TableFollower')
    run_csv_job('example/sample_data/sample_column_usage.csv',
                'test_usage_metadata',
                'databuilder.models.table_column_usage.ColumnReader')
    run_csv_job('example/sample_data/sample_user.csv', 'test_user_metadata',
                'databuilder.models.user.User')
    run_csv_job('example/sample_data/sample_table_report.csv',
                'test_report_metadata',
                'databuilder.models.report.ResourceReport')
    run_csv_job('example/sample_data/sample_source.csv',
                'test_source_metadata',
                'databuilder.models.table_source.TableSource')
    run_csv_job('example/sample_data/sample_tags.csv', 'test_tag_metadata',
                'databuilder.models.table_metadata.TagMetadata')
    run_csv_job('example/sample_data/sample_table_last_updated.csv',
                'test_table_last_updated_metadata',
                'databuilder.models.table_last_updated.TableLastUpdated')
    run_csv_job('example/sample_data/sample_schema_description.csv',
                'test_schema_description',
                'databuilder.models.schema.schema.SchemaModel')
    run_csv_job(
        'example/sample_data/sample_dashboard_base.csv', 'test_dashboard_base',
        'databuilder.models.dashboard.dashboard_metadata.DashboardMetadata')
    run_csv_job('example/sample_data/sample_dashboard_usage.csv',
                'test_dashboard_usage',
                'databuilder.models.dashboard.dashboard_usage.DashboardUsage')
    run_csv_job('example/sample_data/sample_dashboard_owner.csv',
                'test_dashboard_owner',
                'databuilder.models.dashboard.dashboard_owner.DashboardOwner')
    run_csv_job('example/sample_data/sample_dashboard_query.csv',
                'test_dashboard_query',
                'databuilder.models.dashboard.dashboard_query.DashboardQuery')
    run_csv_job(
        'example/sample_data/sample_dashboard_last_execution.csv',
        'test_dashboard_last_execution',
        'databuilder.models.dashboard.dashboard_execution.DashboardExecution')
    run_csv_job(
        'example/sample_data/sample_dashboard_last_modified.csv',
        'test_dashboard_last_modified',
        'databuilder.models.dashboard.dashboard_last_modified.DashboardLastModifiedTimestamp'
    )
    run_csv_job('example/sample_data/sample_dashboard_chart.csv',
                'test_dashboard_chart',
                'databuilder.models.dashboard.dashboard_chart.DashboardChart')
    run_csv_job('example/sample_data/sample_feature_metadata.csv',
                'test_feature_metadata',
                'databuilder.models.feature.feature_metadata.FeatureMetadata')
    run_csv_job(
        'example/sample_data/sample_feature_generation_code.csv',
        'test_feature_generation_code',
        'databuilder.models.feature.feature_generation_code.FeatureGenerationCode'
    )
    run_csv_job(
        'example/sample_data/sample_feature_watermark.csv',
        'test_feature_watermark',
        'databuilder.models.feature.feature_watermark.FeatureWatermark')

    run_table_query_job('example/sample_data/sample_user.csv',
                        'example/sample_data/sample_col.csv',
                        'example/sample_data/sample_table.csv',
                        'example/sample_data/sample_table_query.csv')

    run_table_join_job('example/sample_data/sample_user.csv',
                       'example/sample_data/sample_col.csv',
                       'example/sample_data/sample_table.csv',
                       'example/sample_data/sample_table_query.csv',
                       'example/sample_data/sample_table_query_join.csv')

    run_table_where_job('example/sample_data/sample_user.csv',
                        'example/sample_data/sample_col.csv',
                        'example/sample_data/sample_table.csv',
                        'example/sample_data/sample_table_query.csv',
                        'example/sample_data/sample_table_query_where.csv')

    run_table_execution_job(
        'example/sample_data/sample_user.csv',
        'example/sample_data/sample_col.csv',
        'example/sample_data/sample_table.csv',
        'example/sample_data/sample_table_query.csv',
        'example/sample_data/sample_table_query_execution.csv')

    create_application_job().launch()
    create_dashboard_tables_job().launch()

    create_last_updated_job().launch()

    # with ElasticsearchPublisher, which will be deprecated
    job_es_table = create_es_publisher_sample_job(
        elasticsearch_index_alias='table_search_index',
        elasticsearch_doc_type_key='table',
        entity_type='table',
        model_name=
        'databuilder.models.table_elasticsearch_document.TableESDocument')
    job_es_table.launch()

    job_es_user = create_es_publisher_sample_job(
        elasticsearch_index_alias='user_search_index',
        elasticsearch_doc_type_key='user',
        model_name=
        'databuilder.models.user_elasticsearch_document.UserESDocument',
        entity_type='user',
        elasticsearch_mapping=USER_INDEX_MAP)
    job_es_user.launch()

    job_es_dashboard = create_es_publisher_sample_job(
        elasticsearch_index_alias='dashboard_search_index',
        elasticsearch_doc_type_key='dashboard',
        model_name=
        'databuilder.models.dashboard_elasticsearch_document.DashboardESDocument',
        entity_type='dashboard',
        elasticsearch_mapping=DASHBOARD_ELASTICSEARCH_INDEX_MAPPING)
    job_es_dashboard.launch()

    # with SearchMetadatatoElasticasearchTask
    for resource_type in ['table', 'dashboard', 'user', 'feature']:
        run_search_metadata_task(resource_type)
