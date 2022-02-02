# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from datetime import date
import logging
from typing import Generator, Iterator
from uuid import uuid4

from pyhocon import ConfigTree

from elasticsearch_dsl.connections import connections, Connections
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl.document import Document
from elasticsearch_dsl.index import Index

from databuilder import Scoped
from databuilder.task.base_task import Task
from databuilder.extractor.base_extractor import Extractor
from databuilder.task.search.document_mappings import SearchableResource
from databuilder.transformer.base_transformer import NoopTransformer, Transformer
from databuilder.utils.closer import Closer

from databuilder.task.search.document_mappings import RESOURCE_TO_MAPPING

LOGGER = logging.getLogger(__name__)


class SearchMetadatatoElasticasearchTask(Task):

    ENTITY_TYPE = 'doc_type'
    ELASTICSEARCH_CLIENT_CONFIG_KEY = 'client'
    MAPPING_CLASS = 'document_mapping'
    ELASTICSEARCH_ALIAS_CONFIG_KEY = 'alias'
    ELASTICSEARCH_PUBLISHER_BATCH_SIZE = 'batch_size'
    DATE_STAMP = 'date_stamp'

    DEFAULT_ENTITY_TYPE = 'table'

    today = date.today().strftime("%Y/%m/%d")

    def __init__(self,
                 extractor: Extractor,
                 transformer: Transformer = NoopTransformer()) -> None:
        self.extractor = extractor
        self.transformer = transformer

        self._closer = Closer()
        self._closer.register(self.extractor.close)
        self._closer.register(self.transformer.close)

    def init(self, conf: ConfigTree) -> None:
        # initialize extractor with configurarion
        self.extractor.init(Scoped.get_scoped_conf(conf, self.extractor.get_scope()))
        # initialize transformer with configuration
        self.transformer.init(Scoped.get_scoped_conf(conf, self.transformer.get_scope()))

        # task configuration
        conf = Scoped.get_scoped_conf(conf, self.get_scope())
        self.date_stamp = conf.get_string(SearchMetadatatoElasticasearchTask.DATE_STAMP, self.today)
        self.entity = conf.get_string(SearchMetadatatoElasticasearchTask.ENTITY_TYPE,
                                      self.DEFAULT_ENTITY_TYPE).lower()
        self.elasticsearch_client = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_CLIENT_CONFIG_KEY
        )
        self.elasticsearch_alias = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_ALIAS_CONFIG_KEY
        )
        hex_string = uuid4().hex
        self.elasticsearch_new_index = f"{self.elasticsearch_alias}_{self.date_stamp}_{hex_string}"

        self.document_mapping = conf.get(SearchMetadatatoElasticasearchTask.MAPPING_CLASS,
                                         RESOURCE_TO_MAPPING[self.DEFAULT_ENTITY_TYPE])

        LOGGER.info(issubclass(self.document_mapping, SearchableResource))

        if not issubclass(self.document_mapping, SearchableResource):
            msg = "Provided document_mapping should be instance" \
                f" of SearchableResource not {type(self.document_mapping)}"
            LOGGER.error(msg)
            raise TypeError(msg)

        self.elasticsearch_batch_size = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_PUBLISHER_BATCH_SIZE, 10000)

    def to_document(self, document_mapping: Document, metadata: Iterator, index: str) -> Document:
        return document_mapping(_index=index, **metadata)

    def generate_documents(self, record: Iterator) -> Generator:
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
            index = Index(name=self.elasticsearch_new_index, using=self.elasticsearch_client)
            index.document(self.document_mapping)
            index.create()

            # publish search metadata to ES
            cnt = 0
            for success, info in parallel_bulk(connection,
                                               self.generate_documents(record=record),
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
