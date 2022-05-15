# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import os
import sys

from elasticsearch import Elasticsearch
from pyhocon import ConfigFactory

from databuilder.extractor.nebula_search_data_extractor import NebulaSearchDataExtractor
from databuilder.job.job import DefaultJob
from databuilder.task.search.search_metadata_to_elasticsearch_task import SearchMetadatatoElasticasearchTask

es_host = os.getenv('CREDENTIALS_ELASTICSEARCH_PROXY_HOST', 'localhost')
NEBULA_ENDPOINTS = os.getenv('CREDENTIALS_NEBULA_ENDPOINTS', 'localhost:9669')

nebula_space = os.getenv('NEBULA_SPACE', 'amundsen')
es_port = os.getenv('CREDENTIALS_ELASTICSEARCH_PROXY_PORT', 9200)

if len(sys.argv) > 1:
    es_host = sys.argv[1]
if len(sys.argv) > 2:
    nebula_endpoints = sys.argv[2]

es = Elasticsearch([
    {'host': es_host, 'port': es_port},
])

nebula_endpoints = NEBULA_ENDPOINTS

nebula_user = 'root'
nebula_password = 'nebula'


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
    for resource_type in ['table', 'dashboard', 'user', 'feature']:
        run_search_metadata_task(resource_type)
