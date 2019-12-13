"""
This is a example script which demo how to load data into neo4j without using Airflow DAG.
"""
from pyhocon import ConfigFactory
import os
import random
import textwrap

from databuilder.extractor.neo4j_dashboard_search_data_extractor import Neo4jDashboardSearchDataExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.publisher.elasticsearch_publisher import ElasticsearchPublisher
from databuilder.task.task import DefaultTask
from elasticsearch import Elasticsearch

# set env ES_HOST to override localhost
es = Elasticsearch([
    {'host': os.getenv('ES_HOST', 'localhost')},
])

# set env NEO4J_HOST to override localhost
NEO4J_ENDPOINT = 'bolt://{}:7687'.format(os.getenv('NEO4J_HOST', 'localhost'))
neo4j_endpoint = NEO4J_ENDPOINT

neo4j_user = 'neo4j'
neo4j_password = 'test'

DASHBOARD_ES_MAP = textwrap.dedent(
    """
    {
    "mappings":{
        "dashboard":{
          "properties": {
            "dashboard_group": {
              "type":"text",
              "analyzer": "simple",
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              }
            },
            "dashboard_name": {
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
            "last_reload_time": {
              "type": "date",
              "format": "YYYY-MM-DD'T'HH:mm"
            },
            "user_id": {
              "type": "text",
              "analyzer": "simple"
            },
            "user_name": {
              "type": "text",
              "analyzer": "simple"
            },
            "tags": {
              "type": "keyword"
            }
          }
        }
      }
    }
    """
)


# todo: Add a second model
def create_neo4j_es_job():

    tmp_folder = '/var/tmp/amundsen/dashboard/dashboards_search_data.json'

    task = DefaultTask(loader=FSElasticsearchJSONLoader(),
                       extractor=Neo4jDashboardSearchDataExtractor())

    elasticsearch_client = es
    elasticsearch_new_index_key = 'dashboards'
    elasticsearch_new_index_key_type = 'dashboard'
    elasticsearch_index_alias = 'dashboard_search_index'

    rand = str(random.randint(0, 1000))

    job_config = ConfigFactory.from_dict({
        'extractor.dashboard_search_data.extractor.neo4j.{}'.format(Neo4jExtractor.GRAPH_URL_CONFIG_KEY):
            neo4j_endpoint,
        'extractor.dashboard_search_data.extractor.neo4j.{}'.format(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY):
            'databuilder.models.dashboard_elasticsearch_document.DashboardESDocument',
        'extractor.dashboard_search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_USER): neo4j_user,
        'extractor.dashboard_search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_PW): neo4j_password,
        'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_PATH_CONFIG_KEY): tmp_folder,
        'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_MODE_CONFIG_KEY): 'w',
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_PATH_CONFIG_KEY): tmp_folder,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_MODE_CONFIG_KEY): 'r',
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_DOC_TYPE_CONFIG_KEY):
            elasticsearch_new_index_key_type,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_CLIENT_CONFIG_KEY):
            elasticsearch_client,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY):
            elasticsearch_new_index_key + str(rand),
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_ALIAS_CONFIG_KEY):
            elasticsearch_index_alias,
        'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_MAPPING_CONFIG_KEY): DASHBOARD_ES_MAP
    })

    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=ElasticsearchPublisher())
    return job


if __name__ == "__main__":

    job = create_neo4j_es_job()
    job.launch()
