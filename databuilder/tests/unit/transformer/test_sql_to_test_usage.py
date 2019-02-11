import unittest
from typing import no_type_check
from mock import patch
from pyhocon import ConfigFactory

from databuilder.extractor.hive_table_metadata_extractor import HiveTableMetadataExtractor
from databuilder.models.table_column_usage import TableColumnUsage, ColumnReader
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata
from databuilder.transformer.sql_to_table_col_usage_transformer import SqlToTblColUsageTransformer


class TestSqlToTblColUsageTransformer(unittest.TestCase):

    @no_type_check
    def test(self):
        # type: () -> None
        config = ConfigFactory.from_dict({
            SqlToTblColUsageTransformer.DATABASE_NAME: 'database',
            SqlToTblColUsageTransformer.USER_EMAIL_ATTRIBUTE_NAME: 'email',
            SqlToTblColUsageTransformer.SQL_STATEMENT_ATTRIBUTE_NAME: 'statement'
        })

        with patch.object(HiveTableMetadataExtractor, 'extract') as mock_extract,\
                patch.object(HiveTableMetadataExtractor, 'init'):
            mock_extract.side_effect = [
                TableMetadata('hive', 'gold', 'test_schema1', 'test_table1', 'test_table1', [
                    ColumnMetadata('test_id1', 'description of test_table1', 'bigint', 0),
                    ColumnMetadata('test_id2', 'description of test_id2', 'bigint', 1),
                    ColumnMetadata('is_active', None, 'boolean', 2),
                    ColumnMetadata('source', 'description of source', 'varchar', 3),
                    ColumnMetadata('etl_created_at', 'description of etl_created_at', 'timestamp', 4),
                    ColumnMetadata('ds', None, 'varchar', 5)]), None]

            transformer = SqlToTblColUsageTransformer()
            transformer.init(config)
            foo = Foo(email='john@example.com', statement='SELECT foo, bar FROM test_table1')

            actual = transformer.transform(foo)
            expected = TableColumnUsage(col_readers=[ColumnReader(database=u'database', cluster=u'gold',
                                                                  schema='test_schema1',
                                                                  table='test_table1', column='*',
                                                                  user_email='john@example.com')])
            self.assertEqual(expected.__repr__(), actual.__repr__())


class Foo(object):
    def __init__(self, email, statement):
        # type: (str, str) -> None
        self.email = email
        self.statement = statement


if __name__ == '__main__':
    unittest.main()
