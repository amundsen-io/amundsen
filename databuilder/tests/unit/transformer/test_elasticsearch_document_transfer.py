import unittest

from pyhocon import ConfigFactory  # noqa: F401

from databuilder import Scoped
from databuilder.transformer.elasticsearch_document_transformer import ElasticsearchDocumentTransformer
from databuilder.models.elasticsearch_document import ElasticsearchDocument
from databuilder.models.neo4j_data import Neo4jDataResult


class TestElasticsearchDocumentTransformer(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        self.elasticsearch_index = 'test_es_index'
        self.elasticsearch_type = 'test_es_type'
        config_dict = {'transformer.elasticsearch.index': self.elasticsearch_index,
                       'transformer.elasticsearch.doc_type': self.elasticsearch_type}
        self.conf = ConfigFactory.from_dict(config_dict)

    def test_empty_transform(self):
        # type: () -> None
        """
        Test Transform functionality with no data
        """
        transformer = ElasticsearchDocumentTransformer()
        transformer.init(conf=Scoped.get_scoped_conf(conf=self.conf,
                                                     scope=transformer.get_scope()))

        result = transformer.transform(None)  # type: ignore
        self.assertIsNone(result)

    def test_transform_with_dict_object(self):
        # type: () -> None
        """
        Test Transform functionality with Dict object
        """
        transformer = ElasticsearchDocumentTransformer()
        transformer.init(conf=Scoped.get_scoped_conf(conf=self.conf,
                                                     scope=transformer.get_scope()))

        data = dict(test_key="DOES_NOT_MATTER",
                    test_key2="DOES_NOT_MATTER2")

        with self.assertRaises(Exception) as context:
            transformer.transform(data)  # type: ignore
        self.assertTrue("ElasticsearchDocumentTransformer expects record of type 'Neo4jDataResult'!"
                        in context.exception)

    def test_transform_success_case(self):
        # type: () -> None
        """
        Test transform function with Neo4jDataResult Object
        """
        transformer = ElasticsearchDocumentTransformer()
        transformer.init(conf=Scoped.get_scoped_conf(conf=self.conf,
                                                     scope=transformer.get_scope()))

        data = Neo4jDataResult(database="test_database",
                               cluster="test_cluster",
                               schema_name="test_schema_name",
                               table_name="test_table_name",
                               table_key="test_table_key",
                               table_last_updated_epoch=123456789,
                               table_description="test_table_description",
                               column_names=["test_col1", "test_col2"],
                               column_descriptions=["test_col_description1", "test_col_description2"],
                               total_usage=10,
                               unique_usage=5,
                               tag_names=["test_tag1", "test_tag2"])

        result = transformer.transform(data)

        expected = ElasticsearchDocument(elasticsearch_index='test_es_index',
                                         elasticsearch_type='test_es_type',
                                         database="test_database",
                                         cluster="test_cluster",
                                         schema_name="test_schema_name",
                                         table_name="test_table_name",
                                         table_key="test_table_key",
                                         table_last_updated_epoch=123456789,
                                         table_description="test_table_description",
                                         column_names=["test_col1", "test_col2"],
                                         column_descriptions=["test_col_description1",
                                                              "test_col_description2"],
                                         total_usage=10,
                                         unique_usage=5,
                                         tag_names=["test_tag1", "test_tag2"])

        self.assertIsInstance(result, ElasticsearchDocument)
        self.assertDictEqual(vars(result), vars(expected))
