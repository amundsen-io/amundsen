import importlib

from pyhocon import ConfigTree  # noqa: F401
from typing import Optional  # noqa: F401

from databuilder.transformer.base_transformer import Transformer
from databuilder.models.neo4j_data import Neo4jDataResult


class ElasticsearchDocumentTransformer(Transformer):
    """
    Transformer to convert Neo4j Graph data to Elasticsearch index document format
    """
    ELASTICSEARCH_INDEX_CONFIG_KEY = 'index'
    ELASTICSEARCH_DOC_CONFIG_KEY = 'doc_type'
    ELASTICSEARCH_DOC_MODEL_CLASS_KEY = 'model_class'

    def init(self, conf):
        # type: (ConfigTree) -> None
        self.conf = conf

        self.elasticsearch_index = self.conf.get_string(ElasticsearchDocumentTransformer.ELASTICSEARCH_INDEX_CONFIG_KEY)
        self.elasticsearch_type = self.conf.get_string(ElasticsearchDocumentTransformer.ELASTICSEARCH_DOC_CONFIG_KEY)

        model_class = self.conf.get_string(ElasticsearchDocumentTransformer.ELASTICSEARCH_DOC_MODEL_CLASS_KEY, '')

        if not model_class:
            raise Exception('User needs to provide the ElasticsearchDocument model class')

        module_name, class_name = model_class.rsplit(".", 1)
        mod = importlib.import_module(module_name)
        self.model_class = getattr(mod, class_name)

    def transform(self, record):
        # type: (Neo4jDataResult) -> Optional[ElasticsearchDocument]
        if not record:
            return None

        if not isinstance(record, Neo4jDataResult):
            raise Exception("ElasticsearchDocumentTransformer expects record of type 'Neo4jDataResult'!")

        elasticsearch_obj = self.model_class(elasticsearch_index=self.elasticsearch_index,
                                             elasticsearch_type=self.elasticsearch_type,
                                             **vars(record))

        return elasticsearch_obj

    def get_scope(self):
        # type: () -> str
        return 'transformer.elasticsearch'
