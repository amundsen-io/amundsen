import copy
import unittest

from databuilder.models.table_metadata import ColumnMetadata, TableMetadata


class TestTableMetadata(unittest.TestCase):
    def setUp(self):
        # type: () -> None
        self.table_metadata = TableMetadata('hive', 'gold', 'test_schema1', 'test_table1', 'test_table1', [
            ColumnMetadata('test_id1', 'description of test_table1', 'bigint', 0),
            ColumnMetadata('test_id2', 'description of test_id2', 'bigint', 1),
            ColumnMetadata('is_active', None, 'boolean', 2),
            ColumnMetadata('source', 'description of source', 'varchar', 3),
            ColumnMetadata('etl_created_at', 'description of etl_created_at', 'timestamp', 4),
            ColumnMetadata('ds', None, 'varchar', 5)])

        self.table_metadata2 = TableMetadata('hive', 'gold', 'test_schema1', 'test_table1', 'test_table1', [
            ColumnMetadata('test_id1', 'description of test_table1', 'bigint', 0),
            ColumnMetadata('test_id2', 'description of test_id2', 'bigint', 1),
            ColumnMetadata('is_active', None, 'boolean', 2),
            ColumnMetadata('source', 'description of source', 'varchar', 3),
            ColumnMetadata('etl_created_at', 'description of etl_created_at', 'timestamp', 4),
            ColumnMetadata('ds', None, 'varchar', 5)])

        self.table_metadata3 = TableMetadata('hive', 'gold', 'test_schema3', 'test_table3', 'test_table3', [
            ColumnMetadata('test_id1', 'description of test_table1', 'bigint', 0),
            ColumnMetadata('test_id2', 'description of test_id2', 'bigint', 1),
            ColumnMetadata('is_active', None, 'boolean', 2),
            ColumnMetadata('source', 'description of source', 'varchar', 3),
            ColumnMetadata('etl_created_at', 'description of etl_created_at', 'timestamp', 4),
            ColumnMetadata('ds', None, 'varchar', 5)], is_view=False, attr1='uri', attr2='attr2')

        self.table_metadata4 = TableMetadata('hive', 'gold', 'test_schema4', 'test_table4', 'test_table4', [
            ColumnMetadata('test_id1', 'description of test_table1', 'bigint', 0, ['col-tag1', 'col-tag2'])],
            is_view=False, tags=['tag1', 'tag2'], attr1='uri', attr2='attr2')

        self.expected_nodes_deduped = [
            {'name': 'test_table1', 'KEY': 'hive://gold.test_schema1/test_table1', 'LABEL': 'Table',
             'is_view:UNQUOTED': False},
            {'description': 'test_table1', 'KEY': 'hive://gold.test_schema1/test_table1/_description',
             'LABEL': 'Description'},
            {'sort_order': 0, 'type': 'bigint', 'name': 'test_id1',
             'KEY': 'hive://gold.test_schema1/test_table1/test_id1', 'LABEL': 'Column'},
            {'description': 'description of test_table1',
             'KEY': 'hive://gold.test_schema1/test_table1/test_id1/_description', 'LABEL': 'Description'},
            {'sort_order': 1, 'type': 'bigint', 'name': 'test_id2',
             'KEY': 'hive://gold.test_schema1/test_table1/test_id2', 'LABEL': 'Column'},
            {'description': 'description of test_id2',
             'KEY': 'hive://gold.test_schema1/test_table1/test_id2/_description', 'LABEL': 'Description'},
            {'sort_order': 2, 'type': 'boolean', 'name': 'is_active',
             'KEY': 'hive://gold.test_schema1/test_table1/is_active', 'LABEL': 'Column'},
            {'sort_order': 3, 'type': 'varchar', 'name': 'source', 'KEY': 'hive://gold.test_schema1/test_table1/source',
             'LABEL': 'Column'},
            {'description': 'description of source', 'KEY': 'hive://gold.test_schema1/test_table1/source/_description',
             'LABEL': 'Description'},
            {'sort_order': 4, 'type': 'timestamp', 'name': 'etl_created_at',
             'KEY': 'hive://gold.test_schema1/test_table1/etl_created_at', 'LABEL': 'Column'},
            {'description': 'description of etl_created_at',
             'KEY': 'hive://gold.test_schema1/test_table1/etl_created_at/_description', 'LABEL': 'Description'},
            {'sort_order': 5, 'type': 'varchar', 'name': 'ds', 'KEY': 'hive://gold.test_schema1/test_table1/ds',
             'LABEL': 'Column'}
        ]

        self.expected_nodes = copy.deepcopy(self.expected_nodes_deduped)
        self.expected_nodes.append({'name': 'hive', 'KEY': 'database://hive', 'LABEL': 'Database'})
        self.expected_nodes.append({'name': 'gold', 'KEY': 'hive://gold', 'LABEL': 'Cluster'})
        self.expected_nodes.append({'name': 'test_schema1', 'KEY': 'hive://gold.test_schema1', 'LABEL': 'Schema'})

        self.expected_rels_deduped = [
            {'END_KEY': 'hive://gold.test_schema1/test_table1', 'START_LABEL': 'Schema', 'END_LABEL': 'Table',
             'START_KEY': 'hive://gold.test_schema1', 'TYPE': 'TABLE', 'REVERSE_TYPE': 'TABLE_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/_description', 'START_LABEL': 'Table',
             'END_LABEL': 'Description', 'START_KEY': 'hive://gold.test_schema1/test_table1', 'TYPE': 'DESCRIPTION',
             'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/test_id1', 'START_LABEL': 'Table',
             'END_LABEL': 'Column', 'START_KEY': 'hive://gold.test_schema1/test_table1', 'TYPE': 'COLUMN',
             'REVERSE_TYPE': 'COLUMN_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/test_id1/_description', 'START_LABEL': 'Column',
             'END_LABEL': 'Description', 'START_KEY': 'hive://gold.test_schema1/test_table1/test_id1',
             'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/test_id2', 'START_LABEL': 'Table', 'END_LABEL': 'Column',
             'START_KEY': 'hive://gold.test_schema1/test_table1', 'TYPE': 'COLUMN', 'REVERSE_TYPE': 'COLUMN_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/test_id2/_description', 'START_LABEL': 'Column',
             'END_LABEL': 'Description', 'START_KEY': 'hive://gold.test_schema1/test_table1/test_id2',
             'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/is_active', 'START_LABEL': 'Table', 'END_LABEL': 'Column',
             'START_KEY': 'hive://gold.test_schema1/test_table1', 'TYPE': 'COLUMN', 'REVERSE_TYPE': 'COLUMN_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/source', 'START_LABEL': 'Table', 'END_LABEL': 'Column',
             'START_KEY': 'hive://gold.test_schema1/test_table1', 'TYPE': 'COLUMN', 'REVERSE_TYPE': 'COLUMN_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/source/_description', 'START_LABEL': 'Column',
             'END_LABEL': 'Description', 'START_KEY': 'hive://gold.test_schema1/test_table1/source',
             'TYPE': 'DESCRIPTION',
             'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/etl_created_at', 'START_LABEL': 'Table',
             'END_LABEL': 'Column', 'START_KEY': 'hive://gold.test_schema1/test_table1', 'TYPE': 'COLUMN',
             'REVERSE_TYPE': 'COLUMN_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/etl_created_at/_description', 'START_LABEL': 'Column',
             'END_LABEL': 'Description', 'START_KEY': 'hive://gold.test_schema1/test_table1/etl_created_at',
             'TYPE': 'DESCRIPTION', 'REVERSE_TYPE': 'DESCRIPTION_OF'},
            {'END_KEY': 'hive://gold.test_schema1/test_table1/ds', 'START_LABEL': 'Table', 'END_LABEL': 'Column',
             'START_KEY': 'hive://gold.test_schema1/test_table1', 'TYPE': 'COLUMN', 'REVERSE_TYPE': 'COLUMN_OF'}
        ]

        self.expected_rels = copy.deepcopy(self.expected_rels_deduped)
        self.expected_rels.append({'END_KEY': 'hive://gold', 'START_LABEL': 'Database', 'END_LABEL': 'Cluster',
                                   'START_KEY': 'database://hive', 'TYPE': 'CLUSTER', 'REVERSE_TYPE': 'CLUSTER_OF'})
        self.expected_rels.append({'END_KEY': 'hive://gold.test_schema1', 'START_LABEL': 'Cluster',
                                   'END_LABEL': 'Schema', 'START_KEY': 'hive://gold',
                                   'TYPE': 'SCHEMA', 'REVERSE_TYPE': 'SCHEMA_OF'})

    def test_serialize(self):
        # type: () -> None
        node_row = self.table_metadata.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.table_metadata.next_node()

        self.assertEqual(self.expected_nodes, actual)

        relation_row = self.table_metadata.next_relation()
        actual = []
        while relation_row:
            actual.append(relation_row)
            relation_row = self.table_metadata.next_relation()

        self.assertEqual(self.expected_rels, actual)

        # 2nd record should not show already serialized database, cluster, and schema
        node_row = self.table_metadata2.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.table_metadata2.next_node()

        self.assertEqual(self.expected_nodes_deduped, actual)

        relation_row = self.table_metadata2.next_relation()
        actual = []
        while relation_row:
            actual.append(relation_row)
            relation_row = self.table_metadata2.next_relation()

        self.assertEqual(self.expected_rels_deduped, actual)

        # Test additional K/V Attributes
        node_row = self.table_metadata3.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.table_metadata3.next_node()

        self.assertEqual(actual[0].get('attr1'), 'uri')
        self.assertEqual(actual[0].get('attr2'), 'attr2')

        # Test tag field
        node_row = self.table_metadata4.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = self.table_metadata4.next_node()

        self.assertEqual(actual[0].get('attr1'), 'uri')
        self.assertEqual(actual[0].get('attr2'), 'attr2')

        self.assertEqual(actual[2].get('LABEL'), 'Tag')
        self.assertEqual(actual[2].get('KEY'), 'tag1')
        self.assertEqual(actual[3].get('KEY'), 'tag2')
        self.assertEqual(actual[6].get('KEY'), 'col-tag1')
        self.assertEqual(actual[7].get('KEY'), 'col-tag2')

        relation_row = self.table_metadata4.next_relation()
        actual = []
        while relation_row:
            actual.append(relation_row)
            relation_row = self.table_metadata4.next_relation()

        # Table tag relationship
        expected_tab_tag_rel1 = {'END_KEY': 'tag1', 'START_LABEL': 'Table', 'END_LABEL':
                                 'Tag', 'START_KEY': 'hive://gold.test_schema4/test_table4',
                                 'TYPE': 'TAGGED_BY', 'REVERSE_TYPE': 'TAG'}
        expected_tab_tag_rel2 = {'END_KEY': 'tag2', 'START_LABEL': 'Table',
                                 'END_LABEL': 'Tag', 'START_KEY': 'hive://gold.test_schema4/test_table4',
                                 'TYPE': 'TAGGED_BY', 'REVERSE_TYPE': 'TAG'}
        expected_col_tag_rel1 = {'END_KEY': 'col-tag1', 'START_LABEL': 'Table',
                                 'END_LABEL': 'Tag',
                                 'START_KEY': 'hive://gold.test_schema4/test_table4',
                                 'TYPE': 'TAGGED_BY', 'REVERSE_TYPE': 'TAG'}
        expected_col_tag_rel2 = {'END_KEY': 'col-tag2', 'START_LABEL': 'Table',
                                 'END_LABEL': 'Tag',
                                 'START_KEY': 'hive://gold.test_schema4/test_table4',
                                 'TYPE': 'TAGGED_BY', 'REVERSE_TYPE': 'TAG'}
        self.assertEqual(actual[2], expected_tab_tag_rel1)
        self.assertEqual(actual[3], expected_tab_tag_rel2)
        self.assertEqual(actual[6], expected_col_tag_rel1)
        self.assertEqual(actual[7], expected_col_tag_rel2)


if __name__ == '__main__':
    unittest.main()
