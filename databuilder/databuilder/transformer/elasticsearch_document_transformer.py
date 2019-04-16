from pyhocon import ConfigTree  # noqa: F401
from typing import Optional  # noqa: F401

from databuilder.transformer.base_transformer import Transformer
from databuilder.models.table_elasticsearch_document import TableESDocument
from databuilder.models.user_elasticsearch_document import UserESDocument
from databuilder.models.neo4j_data import Neo4jDataResult


class ElasticsearchDocumentTransformer(Transformer):
    """
    Transformer to convert Neo4j Graph data to Elasticsearch index document format
    """
    ELASTICSEARCH_INDEX_CONFIG_KEY = 'index'
    ELASTICSEARCH_DOC_CONFIG_KEY = 'doc_type'
    ELASTICSEARCH_RESOURCE_CONFIG_KEY = 'resource_type'
    RESOURCE_TYPE_MAPPING = {
        'table',
        'user'
    }

    def init(self, conf):
        # type: (ConfigTree) -> None
        self.conf = conf

        self.elasticsearch_index = self.conf.get_string(ElasticsearchDocumentTransformer.ELASTICSEARCH_INDEX_CONFIG_KEY)
        self.elasticsearch_type = self.conf.get_string(ElasticsearchDocumentTransformer.ELASTICSEARCH_DOC_CONFIG_KEY)
        # values: table, user
        self.elasticsearch_resource_type = self.conf.get_string(ElasticsearchDocumentTransformer.
                                                                ELASTICSEARCH_RESOURCE_CONFIG_KEY,
                                                                'table')

    def transform(self, record):
        # type: (Neo4jDataResult) -> Optional[ElasticsearchDocument]
        if not record:
            return None

        if not isinstance(record, Neo4jDataResult):
            raise Exception("ElasticsearchDocumentTransformer expects record of type 'Neo4jDataResult'!")

        if self.elasticsearch_resource_type.lower() not in \
                ElasticsearchDocumentTransformer.RESOURCE_TYPE_MAPPING:
            raise Exception('resource type needs to define in RESOURCE_TYPE_MAPPING')

        if self.elasticsearch_resource_type == 'table':
            elasticsearch_obj = TableESDocument(elasticsearch_index=self.elasticsearch_index,
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
        elif self.elasticsearch_resource_type == 'user':
            elasticsearch_obj = UserESDocument(elasticsearch_index=self.elasticsearch_index,
                                               elasticsearch_type=self.elasticsearch_type,
                                               email=record.email,
                                               first_name=record.first_name,
                                               last_name=record.last_name,
                                               name=record.name,
                                               github_username=record.github_username,
                                               team_name=record.team_name,
                                               employee_type=record.employee_type,
                                               manager_email=record.manager_email,
                                               slack_id=record.slack_id,
                                               is_active=record.is_active,
                                               total_read=record.total_read,
                                               total_own=record.total_own,
                                               total_follow=record.total_follow,
                                               )
        else:
            raise NotImplementedError()

        return elasticsearch_obj

    def get_scope(self):
        # type: () -> str
        return 'transformer.elasticsearch'
