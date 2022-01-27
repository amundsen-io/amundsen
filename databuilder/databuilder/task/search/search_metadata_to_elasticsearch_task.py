# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Dict, Iterator
from databuilder.databuilder.publisher.neo4j_csv_publisher import DEFAULT_CONFIG
from databuilder.databuilder.task.search.document_mappings import SearchableResource

from pyhocon import ConfigFactory, ConfigTree

from elasticsearch_dsl.connections import connections, Connections
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl.document import Document
from elasticsearch_dsl.index import Index

from databuilder import Scoped
from databuilder.task.base_task import Task
from databuilder.extractor.base_extractor import Extractor
from databuilder.transformer.base_transformer import NoopTransformer, Transformer
from databuilder.utils.closer import Closer

from databuilder.task.search.document_mappings import RESOURCE_TO_MAPPING, DefaultIndex

LOGGER = logging.getLogger(__name__)


class SearchMetadatatoElasticasearchTask(Task):

    ENTITY_TYPE = 'doc_type'
    ELASTICSEARCH_CLIENT_CONFIG_KEY = 'client'
    CUSTOM_INDEX_CLASS = 'custom_index'
    MAPPING_CLASS = 'document_mapping'
    ELASTICSEARCH_NEW_INDEX_CONFIG_KEY = 'new_index'
    ELASTICSEARCH_ALIAS_CONFIG_KEY = 'alias'
    ELASTICSEARCH_PUBLISHER_BATCH_SIZE = 'batch_size'

    DEFAULT_ENTITY_TYPE = 'table'

    DEFAULT_CONFIG = ConfigFactory.from_dict({
        ENTITY_TYPE: DEFAULT_ENTITY_TYPE,
        CUSTOM_INDEX_CLASS: DefaultIndex,
        MAPPING_CLASS: RESOURCE_TO_MAPPING[DEFAULT_ENTITY_TYPE],
        ELASTICSEARCH_PUBLISHER_BATCH_SIZE: 10000
    })

    def __init__(self,
                 extractor: Extractor,
                 transformer: Transformer = NoopTransformer()) -> None:
        self.extractor = extractor
        self.transformer = transformer

        self._closer = Closer()
        self._closer.register(self.extractor.close)
        self._closer.register(self.transformer.close)

    def init(self, conf: ConfigTree) -> None:
        self.extractor.init(Scoped.get_scoped_conf(conf, self.extractor.get_scope()))
        self.transformer.init(Scoped.get_scoped_conf(conf, self.transformer.get_scope()))

        conf = Scoped.get_scoped_conf(conf, self.get_scope()).with_fallback(DEFAULT_CONFIG)

        self.entity = conf.get_string(SearchMetadatatoElasticasearchTask.ENTITY_TYPE).lower()
        self.elasticsearch_client = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_CLIENT_CONFIG_KEY
        )

        self.elasticsearch_new_index = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY
        )
        self.elasticsearch_alias = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_ALIAS_CONFIG_KEY
        )
        self.index_class = conf.get(SearchMetadatatoElasticasearchTask.CUSTOM_INDEX_CLASS)
        self.document_mapping = conf.get(SearchMetadatatoElasticasearchTask.MAPPING_CLASS)
        if not isinstance(self.document_mapping, SearchableResource):
            msg = "Provided document_mapping should be instance" \
                f" of SearchableResource not {type(self.document_mapping)}"
            LOGGER.error(msg)
            raise TypeError(msg)

        self.elasticsearch_batch_size = conf.get(SearchMetadatatoElasticasearchTask.ELASTICSEARCH_PUBLISHER_BATCH_SIZE)

    def to_document(self, document_mapping: Document, metadata: Dict, index: str) -> Document:
        return document_mapping(_index=index, **metadata)

    def generator(self, record: Iterator) -> Dict:
        # iterate through records
        while record:
            record = self.transformer.transform(record)
            if not record:
                # Move on if the transformer filtered the record out
                record = self.extractor.extract()
                continue
            yield self.to_document(document_mapping=self.document_mapping,
                                   metadata=record,
                                   index=self.elasticsearch_new_index).to_dict(True)
            record = self.extractor.extract()

    def _delete_old_index(self, connection: Connections, document_index: Index) -> None:
        alias_updates = [
            {"add": {"index": document_index._name, "alias": self.elasticsearch_alias}}
        ]
        for index_name in connection.indices.get_alias():
            if index_name.startswith(f"{self.elasticsearch_alias}_"):
                if index_name != document_index._name:
                    LOGGER.info(f"Deleting index old {index_name}")
                    alias_updates.append({"remove_index": {"index": index_name}})
        connection.indices.update_aliases({"actions": alias_updates})

    def run(self) -> None:
        LOGGER.info('Running search metadata to Elasticsearch task')
        try:
            # create connection
            connections.add_connection('default', self.elasticsearch_client)
            connection = connections.get_connection()

            # health check ES
            health = connection.cluster.health()
            status = health["status"]
            if status not in ("green", "yellow"):
                msg = f"Elasticsearch healthcheck failed: {status}"
                LOGGER.error(msg)
                raise Exception(msg)

            # extract records from metadata store
            record = self.extractor.extract()

            # create index
            LOGGER.info(f"Creating ES index {self.elasticsearch_new_index}")
            index = self.index_class(name=self.elasticsearch_new_index)

            # publish search metadata to ES
            cnt = 0
            for success, info in parallel_bulk(connection,
                                               self.generator(record=record),
                                               raise_on_error=False,
                                               chunk_size=self.elasticsearch_batch_size):
                if not success:
                    LOGGER.warn(f"There was an error while indexing a document to ES: {info}")
                else:
                    cnt += 1
                if cnt == self.elasticsearch_batch_size:
                    LOGGER.info(f'Published {str(cnt)} records to ES')

            # delete old index
            self._delete_old_index(connection=connection,
                                   document_index=index)

            LOGGER.info("Elasticsearch Indexing completed")
        finally:
            self._closer.close()

    def get_scope(self) -> str:
        return 'task.search_metadata_to_elasticsearch'
