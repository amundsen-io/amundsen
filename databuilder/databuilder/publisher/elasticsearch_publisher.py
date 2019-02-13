import json
import logging
import textwrap
from typing import List  # noqa: F401

from pyhocon import ConfigTree  # noqa: F401
from elasticsearch.exceptions import NotFoundError

from databuilder.publisher.base_publisher import Publisher

LOGGER = logging.getLogger(__name__)


class ElasticsearchPublisher(Publisher):
    """
    Elasticsearch Publisher uses Bulk API to load data from JSON file.
    A new index is created and data is uploaded into it. After the upload
    is complete, index alias is swapped to point to new index from old index
    and traffic is routed to new index.

    Old index is deleted after the alias swap is complete
    """
    FILE_PATH_CONFIG_KEY = 'file_path'
    FILE_MODE_CONFIG_KEY = 'mode'

    ELASTICSEARCH_CLIENT_CONFIG_KEY = 'client'
    ELASTICSEARCH_NEW_INDEX_CONFIG_KEY = 'new_index'
    ELASTICSEARCH_ALIAS_CONFIG_KEY = 'alias'
    ELASTICSEARCH_MAPPING_CONFIG_KEY = 'mapping'

    # Specifying default mapping for elasticsearch index
    # Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
    # Setting type to "text" for all fields that would be used in search
    # Using Simple Analyzer to convert all text into search terms
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-simple-analyzer.html
    # Standard Analyzer is used for all text fields that don't explicitly specify an analyzer
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-standard-analyzer.html
    DEFAULT_ELASTICSEARCH_INDEX_MAPPING = textwrap.dedent(
        """
        {
        "mappings":{
            "table":{
              "properties": {
                "table_name": {
                  "type":"text",
                  "analyzer": "simple",
                  "fields": {
                    "raw": {
                      "type": "keyword"
                    }
                  }
                },
                "schema_name": {
                  "type":"text",
                  "analyzer": "simple",
                  "fields": {
                    "raw": {
                      "type": "keyword"
                    }
                  }
                },
                "table_last_updated_epoch": {
                  "type": "date",
                  "format": "epoch_second"
                },
                "table_description": {
                  "type": "text",
                  "analyzer": "simple"
                },
                "column_names": {
                  "type":"text",
                  "analyzer": "simple",
                  "fields": {
                    "raw": {
                      "type": "keyword"
                    }
                  }
                },
                "column_descriptions": {
                  "type": "text",
                  "analyzer": "simple"
                },
                "tag_names": {
                  "type": "keyword"
                },
                "cluster": {
                  "type": "text"
                },
                "database": {
                  "type": "text"
                },
                "table_key": {
                  "type": "keyword"
                },
                "total_usage":{
                  "type": "long"
                },
                "unique_usage": {
                  "type": "long"
                }
              }
            }
          }
        }
        """
    )

    def __init__(self):
        # type: () -> None
        pass

    def init(self, conf):
        # type: (ConfigTree) -> None
        self.conf = conf

        self.file_path = self.conf.get_string(ElasticsearchPublisher.FILE_PATH_CONFIG_KEY)
        self.file_mode = self.conf.get_string(ElasticsearchPublisher.FILE_MODE_CONFIG_KEY, 'w')

        self.elasticsearch_client = self.conf.get(ElasticsearchPublisher.ELASTICSEARCH_CLIENT_CONFIG_KEY)
        self.elasticsearch_new_index = self.conf.get(ElasticsearchPublisher.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY)
        self.elasticsearch_alias = self.conf.get(ElasticsearchPublisher.ELASTICSEARCH_ALIAS_CONFIG_KEY)

        self.elasticsearch_mapping = self.conf.get(ElasticsearchPublisher.ELASTICSEARCH_MAPPING_CONFIG_KEY,
                                                   ElasticsearchPublisher.DEFAULT_ELASTICSEARCH_INDEX_MAPPING)

        self.file_handler = open(self.file_path, self.file_mode)

    def _fetch_old_index(self):
        # type: () -> List[str]
        """
        Retrieve all indices that currently have {elasticsearch_alias} alias
        :return: list of elasticsearch indices
        """
        try:
            indices = self.elasticsearch_client.indices.get_alias(self.elasticsearch_alias).keys()
            return indices
        except NotFoundError:
            LOGGER.warn("Received index not found error from Elasticsearch", exc_info=True)
            # return empty list on exception
            return []

    def publish(self):
        # type: () -> None
        """
        Use Elasticsearch Bulk API to load data from file to a {new_index}.
        After upload, swap alias from {old_index} to {new_index} in a atomic operation
        to route traffic to {new_index}
        """
        actions = [json.loads(l) for l in self.file_handler.readlines()]
        # ensure new data exists
        if not actions:
            LOGGER.warning("received no data to upload to Elasticsearch!")
            return

        # create new index with mapping
        self.elasticsearch_client.indices.create(index=self.elasticsearch_new_index, body=self.elasticsearch_mapping)

        # bulk upload data
        self.elasticsearch_client.bulk(actions)

        # fetch indices that have {elasticsearch_alias} as alias
        elasticsearch_old_indices = self._fetch_old_index()

        # update alias to point to the new index
        actions = [{"add": {"index": self.elasticsearch_new_index, "alias": self.elasticsearch_alias}}]

        # delete old indices
        delete_actions = [{"remove_index": {"index": index}} for index in elasticsearch_old_indices]
        actions.extend(delete_actions)

        update_action = {"actions": actions}

        # perform alias update and index delete in single atomic operation
        self.elasticsearch_client.indices.update_aliases(update_action)

    def get_scope(self):
        # type: () -> str
        return 'publisher.elasticsearch'
