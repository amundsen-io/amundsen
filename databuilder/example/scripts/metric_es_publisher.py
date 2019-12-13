"""
This is a example script which demo how to load data into neo4j without using Airflow DAG.
"""
import os
import random
import textwrap

from elasticsearch import Elasticsearch
from pyhocon import ConfigFactory

from databuilder.extractor.neo4j_metric_search_data_extractor import \
    Neo4jMetricSearchDataExtractor
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_elasticsearch_json_loader import \
    FSElasticsearchJSONLoader
from databuilder.publisher.elasticsearch_publisher import \
    ElasticsearchPublisher
from databuilder.task.task import DefaultTask

# set env ES_HOST to override localhost
es = Elasticsearch([
    {'host': os.getenv('ES_HOST', 'localhost')},
])

# set env NEO4J_HOST to override localhost
NEO4J_ENDPOINT = 'bolt://{}:7687'.format(os.getenv('NEO4J_HOST', 'localhost'))
neo4j_endpoint = NEO4J_ENDPOINT

neo4j_user = 'neo4j'
neo4j_password = 'test'

METRIC_ES_MAP = textwrap.dedent(
    """
    {
    "mappings":{
        "metric":{
          "properties": {
            "name": {
              "type":"text",
              "analyzer": "simple",
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              }
            },
            "description": {
              "type": "text",
              "analyzer": "simple"
            },
            "type": {
              "type":"text",
              "analyzer": "simple",
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              }
            },
            "tags": {
              "type": "keyword"
            },
            "dashboards": {
              "type":"text",
              "analyzer": "simple",
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              }
            }
          }
        }
      }
    }
    """
)


# todo: Add a second model
def create_neo4j_es_job():

    tmp_folder = '/var/tmp/amundsen/metric/metric_search_data.json'

    task = DefaultTask(loader=FSElasticsearchJSONLoader(),
                       extractor=Neo4jMetricSearchDataExtractor())

    elasticsearch_client = es
    elasticsearch_new_index_key = 'metrics'
    elasticsearch_new_index_key_type = 'metric'
    elasticsearch_index_alias = 'metric_search_index'

    rand = str(random.randint(0, 1000))

    job_config = ConfigFactory.from_dict({
        'extractor.dashboard_search_data.extractor.neo4j.{}'.format(Neo4jExtractor.GRAPH_URL_CONFIG_KEY):
            neo4j_endpoint,
        'extractor.dashboard_search_data.extractor.neo4j.{}'.format(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY):
            'databuilder.models.metric_elasticsearch_document.MetricESDocument',
        'extractor.dashboard_search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_USER):
            neo4j_user,
        'extractor.dashboard_search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_PW):
            neo4j_password,
        'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_PATH_CONFIG_KEY):
            tmp_folder,
        'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_MODE_CONFIG_KEY):
            'w',
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_PATH_CONFIG_KEY):
            tmp_folder,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_MODE_CONFIG_KEY):
            'r',
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_DOC_TYPE_CONFIG_KEY):
            elasticsearch_new_index_key_type,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_CLIENT_CONFIG_KEY):
            elasticsearch_client,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY):
            elasticsearch_new_index_key + str(rand),
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_ALIAS_CONFIG_KEY):
            elasticsearch_index_alias,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_MAPPING_CONFIG_KEY):
            METRIC_ES_MAP
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=ElasticsearchPublisher())
    return job


if __name__ == "__main__":
    job = create_neo4j_es_job()
    job.launch()
