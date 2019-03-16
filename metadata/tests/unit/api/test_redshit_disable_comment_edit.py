import unittest
from http import HTTPStatus

from mock import patch
from metadata_service.api.table import TableDescriptionAPI
from metadata_service.api.column import ColumnDescriptionAPI


class RedshiftCommentEditDisableTest(unittest.TestCase):
    def test_table_comment_edit(self) -> None:
        with patch('metadata_service.api.table.get_proxy_client'):
            tbl_dscrpt_api = TableDescriptionAPI()

            table_uri = 'hive://gold.test_schema/test_table'
            response = tbl_dscrpt_api.put(table_uri=table_uri, description_val='test')
            self.assertEqual(list(response)[1], HTTPStatus.OK)

    def test_column_comment_edit(self) -> None:
        with patch('metadata_service.api.column.get_proxy_client'):
            col_dscrpt_api = ColumnDescriptionAPI()

            table_uri = 'hive://gold.test_schema/test_table'
            response = col_dscrpt_api.put(table_uri=table_uri, column_name='foo', description_val='test')
            self.assertEqual(list(response)[1], HTTPStatus.OK)


if __name__ == '__main__':
    unittest.main()
