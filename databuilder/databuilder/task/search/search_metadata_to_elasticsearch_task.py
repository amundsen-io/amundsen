# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import date
from typing import (
    Any, Generator, List,
)
from uuid import uuid4

from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl.connections import Connections, connections
from elasticsearch_dsl.document import Document
from elasticsearch_dsl.index import Index
from pyhocon import ConfigTree

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.task.base_task import Task
from databuilder.task.search.document_mappings import RESOURCE_TO_MAPPING, SearchableResource
from databuilder.transformer.base_transformer import NoopTransformer, Transformer
from databuilder.utils.closer import Closer

LOGGER = logging.getLogger(__name__)


class SearchMetadatatoElasticasearchTask(Task):

    ENTITY_TYPE = 'doc_type'
    ELASTICSEARCH_CLIENT_CONFIG_KEY = 'client'
    MAPPING_CLASS = 'document_mapping'
    ELASTICSEARCH_ALIAS_CONFIG_KEY = 'alias'
    ELASTICSEARCH_NEW_INDEX = 'new_index'
    ELASTICSEARCH_PUBLISHER_BATCH_SIZE = 'batch_size'
    ELASTICSEARCH_TIMEOUT_SEC = 'es_timeout_sec'
    DATE = 'date'

    today = date.today().strftime("%Y%m%d")

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
        self.date = conf.get_string(SearchMetadatatoElasticasearchTask.DATE, self.today)
        self.entity = conf.get_string(SearchMetadatatoElasticasearchTask.ENTITY_TYPE).lower()
        self.elasticsearch_client = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_CLIENT_CONFIG_KEY
        )
        self.elasticsearch_alias = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_ALIAS_CONFIG_KEY
        )
        self.elasticsearch_new_index = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_NEW_INDEX,
            self.create_new_index_name())
        self.document_mapping = conf.get(SearchMetadatatoElasticasearchTask.MAPPING_CLASS,
                                         RESOURCE_TO_MAPPING[self.entity])

        if not issubclass(self.document_mapping, SearchableResource):
            msg = "Provided document_mapping should be instance" \
                f" of SearchableResource not {type(self.document_mapping)}"
            LOGGER.error(msg)
            raise TypeError(msg)

        self.elasticsearch_batch_size = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_PUBLISHER_BATCH_SIZE, 10000
        )
        self.elasticsearch_timeout_sec = conf.get(
            SearchMetadatatoElasticasearchTask.ELASTICSEARCH_TIMEOUT_SEC, 120
        )

    def create_new_index_name(self) -> str:
        hex_string = uuid4().hex
        return f"{self.elasticsearch_alias}_{self.date}_{hex_string}"

    def to_document(self, metadata: Any) -> Document:
        return self.document_mapping(_index=self.elasticsearch_new_index,
                                     **metadata)

    def generate_documents(self, record: Any) -> Generator:
        # iterate through records
        while record:
            record = self.transformer.transform(record)
            if not record:
                # Move on if the transformer filtered the record out
                record = self.extractor.extract()
                continue
            document = self.to_document(metadata=record).to_dict(True)
            document['_source']['resource_type'] = self.entity

            yield document
            record = self.extractor.extract()

    def _get_old_index(self, connection: Connections) -> List[str]:
        """
        Retrieve all indices that currently have {elasticsearch_alias} alias
        :return: list of elasticsearch indices
        """
        try:
            indices = connection.indices.get_alias(self.elasticsearch_alias).keys()
            return indices
        except NotFoundError:
            LOGGER.warn("Received index not found error from Elasticsearch. " +
                        "The index doesn't exist for a newly created ES. It's OK on first run.")
            # return empty list on exception
            return []

    def _delete_old_index(self, connection: Connections, document_index: Index) -> None:
        alias_updates = []
        previous_index = self._get_old_index(connection=connection)
        for previous_index_name in previous_index:
            if previous_index_name != document_index._name:
                LOGGER.info(f"Deleting old index {previous_index_name}")
                alias_updates.append({"remove_index": {"index": previous_index_name}})
        alias_updates.append({"add": {
            "index": self.elasticsearch_new_index,
            "alias": self.elasticsearch_alias}})
        connection.indices.update_aliases({"actions": alias_updates})

    def run(self) -> None:
        LOGGER.info('Running search metadata to Elasticsearch task')
        try:
            # extract records from metadata store
            record = self.extractor.extract()

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

            # create index
            LOGGER.info(f"Creating ES index {self.elasticsearch_new_index}")
            index = Index(name=self.elasticsearch_new_index, using=self.elasticsearch_client)
            index.document(self.document_mapping)

            # allow for longer ngram length
            index.settings(max_shingle_diff=10)

            index.create()

            # publish search metadata to ES
            cnt = 0
            for success, info in parallel_bulk(connection,
                                               self.generate_documents(record=record),
                                               raise_on_error=False,
                                               chunk_size=self.elasticsearch_batch_size,
                                               request_timeout=self.elasticsearch_timeout_sec):
                if not success:
                    LOGGER.warn(f"There was an error while indexing a document to ES: {info}")
                else:
                    cnt += 1
                if cnt == self.elasticsearch_batch_size:
                    LOGGER.info(f'Published {str(cnt*self.elasticsearch_batch_size)} records to ES')

            # delete old index
            self._delete_old_index(connection=connection,
                                   document_index=index)

            LOGGER.info("Elasticsearch Indexing completed")
        finally:
            self._closer.close()

    def get_scope(self) -> str:
        return 'task.search_metadata_to_elasticsearch'
