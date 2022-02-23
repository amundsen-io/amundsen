# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import os

from elasticsearch import Elasticsearch
from pyhocon import ConfigFactory

from databuilder.extractor.neo4j_search_data_extractor import Neo4jSearchDataExtractor
from databuilder.job.job import DefaultJob
from databuilder.task.search.search_metadata_to_elasticsearch_task import SearchMetadatatoElasticasearchTask

es_host = os.getenv('CREDENTIALS_ELASTICSEARCH_PROXY_HOST', 'localhost')
neo_host = os.getenv('CREDENTIALS_NEO4J_PROXY_HOST', 'localhost')

es_port = os.getenv('CREDENTIALS_ELASTICSEARCH_PROXY_PORT', 9200)
neo_port = os.getenv('CREDENTIALS_NEO4J_PROXY_PORT', 7687)

es = Elasticsearch([
    {'host': es_host, 'port': es_port},
])

neo4j_endpoint = f'bolt://{neo_host}:{neo_port}'

neo4j_user = 'neo4j'
neo4j_password = 'test'


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
        'extractor.search_data.extractor.neo4j.graph_url':
            neo4j_endpoint,
        'extractor.search_data.extractor.neo4j.neo4j_auth_user':
            neo4j_user,
        'extractor.search_data.extractor.neo4j.neo4j_auth_pw':
            neo4j_password,
        'extractor.search_data.extractor.neo4j.neo4j_encrypted':
            False,
    }

    job_config = ConfigFactory.from_dict({
        **task_config,
    })

    extractor = Neo4jSearchDataExtractor()
    task = SearchMetadatatoElasticasearchTask(extractor=extractor)

    job = DefaultJob(conf=job_config, task=task)

    job.launch()


if __name__ == "__main__":
    for resource_type in ['table', 'dashboard', 'user', 'feature']:
        run_search_metadata_task(resource_type)
