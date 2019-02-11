from pyhocon import ConfigTree  # noqa: F401
from typing import Optional  # noqa: F401

from databuilder.transformer.base_transformer import Transformer
from databuilder.models.elasticsearch_document import ElasticsearchDocument
from databuilder.models.neo4j_data import Neo4jDataResult


class ElasticsearchDocumentTransformer(Transformer):
    """
    Transformer to convert Neo4j Graph data to Elasticsearch index document format
    """
    ELASTICSEARCH_INDEX_CONFIG_KEY = 'index'
    ELASTICSEARCH_DOC_CONFIG_KEY = 'doc_type'

    def init(self, conf):
        # type: (ConfigTree) -> None
        self.conf = conf

        self.elasticsearch_index = self.conf.get_string(ElasticsearchDocumentTransformer.ELASTICSEARCH_INDEX_CONFIG_KEY)
        self.elasticsearch_type = self.conf.get_string(ElasticsearchDocumentTransformer.ELASTICSEARCH_DOC_CONFIG_KEY)

    def transform(self, record):
        # type: (Neo4jDataResult) -> Optional[ElasticsearchDocument]
        if not record:
            return None

        if not isinstance(record, Neo4jDataResult):
            raise Exception("ElasticsearchDocumentTransformer expects record of type 'Neo4jDataResult'!")

        elasticsearch_obj = ElasticsearchDocument(elasticsearch_index=self.elasticsearch_index,
                                                  elasticsearch_type=self.elasticsearch_type,
                                                  database=record.database,
                                                  cluster=record.cluster,
                                                  schema_name=record.schema_name,
                                                  table_name=record.table_name,
                                                  table_key=record.table_key,
                                                  table_description=record.table_description,
                                                  table_last_updated_epoch=record.table_last_updated_epoch,
                                                  column_names=record.column_names,
                                                  column_descriptions=record.column_descriptions,
                                                  total_usage=record.total_usage,
                                                  unique_usage=record.unique_usage,
                                                  tag_names=record.tag_names)
        return elasticsearch_obj

    def get_scope(self):
        # type: () -> str
        return 'transformer.elasticsearch'
