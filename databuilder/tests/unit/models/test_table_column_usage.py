# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.models.table_column_usage import ColumnReader, TableColumnUsage
from typing import no_type_check


class TestTableColumnUsage(unittest.TestCase):

    @no_type_check  # mypy is somehow complaining on assignment on expected dict.
    def test_serialize(self) -> None:

        col_readers = [ColumnReader(database='db', cluster='gold', schema='scm', table='foo', column='*',
                                    user_email='john@example.com')]
        table_col_usage = TableColumnUsage(col_readers=col_readers)

        node_row = table_col_usage.next_node()
        actual = []
        while node_row:
            actual.append(node_row)
            node_row = table_col_usage.next_node()

        expected = [{'first_name': '',
                     'last_name': '',
                     'full_name': '',
                     'employee_type': '',
                     'is_active:UNQUOTED': True,
                     'updated_at': 0,
                     'LABEL': 'User',
                     'slack_id': '',
                     'KEY': 'john@example.com',
                     'github_username': '',
                     'team_name': '',
                     'email': 'john@example.com',
                     'role_name': ''}]
        self.assertEqual(expected, actual)

        rel_row = table_col_usage.next_relation()
        actual = []
        while rel_row:
            actual.append(rel_row)
            rel_row = table_col_usage.next_relation()

        expected = [{'read_count:UNQUOTED': 1, 'END_KEY': 'john@example.com', 'START_LABEL': 'Table',
                     'END_LABEL': 'User', 'START_KEY': 'db://gold.scm/foo', 'TYPE': 'READ_BY', 'REVERSE_TYPE': 'READ'}]
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
