# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Dict, Iterator

from pyhocon import ConfigTree

from elasticsearch_dsl.connections import connections, Connections
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl.document import Document
from elasticsearch_dsl.index import Index

from databuilder import Scoped
from databuilder.task.base_task import Task
from databuilder.extractor.base_extractor import Extractor
from databuilder.transformer.base_transformer import NoopTransformer, Transformer
from databuilder.utils.closer import Closer

from databuilder.task.search.document_mappings import RESOURCE_TO_MAPPING, english_analyzer, stemming_analyzer

LOGGER = logging.getLogger(__name__)


class SearchMetadatatoElasticasearchTask(Task):
    
    
    ELASTICSEARCH_CLIENT_CONFIG_KEY = 'client'
    ENTITY_TYPE = 'doc_type'
    MAPPING = 'document_mapping'
    CUSTOM_ANALYZERS = 'custom_analyzers'
    ELASTICSEARCH_NEW_INDEX_CONFIG_KEY = 'new_index'
    ELASTICSEARCH_ALIAS_CONFIG_KEY = 'alias'

    # config to control how many max documents to publish at a time
    ELASTICSEARCH_PUBLISHER_BATCH_SIZE = 'batch_size'

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

        conf = Scoped.get_scoped_conf(conf, self.get_scope())
        default_analyzers = [english_analyzer, stemming_analyzer]

        self.entity = conf.get_string(SearchMetadatatoElasticasearchTask.ENTITY_TYPE, default='table').lower()
        self.document_mapping = conf.get(SearchMetadatatoElasticasearchTask.MAPPING, RESOURCE_TO_MAPPING[self.entity])
        # not sure if this is the best way to configure custom analyzers since it is not enough to add them to the documents
        self.analyzers = conf.get_list(SearchMetadatatoElasticasearchTask.CUSTOM_ANALYZERS, default_analyzers)

        self.elasticsearch_client = conf.get(SearchMetadatatoElasticasearchTask.ELASTICSEARCH_CLIENT_CONFIG_KEY)
        self.elasticsearch_new_index = conf.get(SearchMetadatatoElasticasearchTask.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY)
        self.elasticsearch_alias = conf.get(SearchMetadatatoElasticasearchTask.ELASTICSEARCH_ALIAS_CONFIG_KEY)

        self.elasticsearch_batch_size = conf.get(SearchMetadatatoElasticasearchTask.ELASTICSEARCH_PUBLISHER_BATCH_SIZE,
                                                      10000)
    
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

    def _create_index(self) -> Index:
        index = Index(self.elasticsearch_new_index)
        LOGGER.info(f"Creating new index {index._name}")
        for analyzer in self.analyzers:
            index.analyzer(analyzer)
        index.create()
        return index
    
    def run(self) -> None:
        """
        Runs a task
        """
        LOGGER.info('Running search metadata to Elasticsearch task')
        try:
            # get ES connection
            connections.add_connection('default', self.elasticsearch_client)
            connection = connections.get_connection()

            # extract records from metadata store
            record = self.extractor.extract()

            # create index
            document_index = self._create_index()
            
            # publish search metadata to ES
            cnt = 0
            for success, info in parallel_bulk(connection,
                                               self.generator(record=record),
                                               raise_on_error=False):
                if not success:
                    LOGGER.warn(f"There was an error while indexing a document to ES {info}")
                else:
                    cnt += 1
                if cnt == self.elasticsearch_batch_size:
                    LOGGER.info(f'Publish {str(cnt)} of records to ES')

            # delete old index
            self._delete_old_index(connection=connection,
                                   document_index=document_index)

            LOGGER.info("Elasticsearch Indexing completed")

        finally:
            self._closer.close()
    
    def get_scope(self) -> str:
        return 'task.search_metadata_to_elasticsearch'
