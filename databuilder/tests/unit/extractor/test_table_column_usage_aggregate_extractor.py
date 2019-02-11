import unittest

from mock import patch, MagicMock  # noqa: F401
from pyhocon import ConfigFactory

from databuilder.extractor.table_column_usage_aggregate_extractor import TblColUsgAggExtractor, RAW_EXTRACTOR
from databuilder.models.table_column_usage import TableColumnUsage, ColumnReader
from databuilder.transformer.regex_str_replace_transformer import RegexStrReplaceTransformer
from databuilder.transformer.sql_to_table_col_usage_transformer import SqlToTblColUsageTransformer


class TestTblColUsgAggExtractor(unittest.TestCase):

    def test_aggregate(self):
        # type: () -> None
        with patch.object(RegexStrReplaceTransformer, 'init'),\
                patch.object(SqlToTblColUsageTransformer, 'init'),\
                patch.object(RegexStrReplaceTransformer, 'transform'),\
                patch.object(SqlToTblColUsageTransformer, 'transform') as mock_sql_transform:

            raw_extractor = MagicMock()
            mock_raw_extractor = MagicMock()
            raw_extractor.extract = mock_raw_extractor
            raw_extractor.get_scope.return_value = 'foo'

            # Just to iterate 5 times
            mock_raw_extractor.side_effect = ['foo', 'bar', 'foo', 'bar', None]

            conf = ConfigFactory.from_dict(
                {RAW_EXTRACTOR: raw_extractor}
            )

            mock_sql_transform.side_effect = [
                TableColumnUsage(col_readers=[ColumnReader(database='database', cluster='gold', schema='test_schema1',
                                                           table='test_table1', column='*',
                                                           user_email='john@example.com')]),
                TableColumnUsage(col_readers=[ColumnReader(database='database', cluster='gold', schema='test_schema1',
                                                           table='test_table1', column='*',
                                                           user_email='john@example.com', read_count=2)]),
                TableColumnUsage(col_readers=[ColumnReader(database='database', cluster='gold', schema='test_schema1',
                                                           table='test_table2', column='*',
                                                           user_email='john@example.com', read_count=5)]),
                None]

            extractor = TblColUsgAggExtractor()
            extractor.init(conf)
            actual = extractor.extract()
            expected = TableColumnUsage(
                col_readers=[
                    ColumnReader(database='database', cluster='gold', schema='test_schema1', table='test_table1',
                                 column='*', user_email='john@example.com', read_count=3),
                    ColumnReader(database='database', cluster='gold', schema='test_schema1', table='test_table2',
                                 column='*', user_email='john@example.com', read_count=5)])

            self.assertEqual(expected.__repr__(), actual.__repr__())


if __name__ == '__main__':
    unittest.main()
