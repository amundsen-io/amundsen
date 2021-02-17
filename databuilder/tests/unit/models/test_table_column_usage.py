# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from typing import no_type_check
from unittest.mock import ANY

from databuilder.models.table_column_usage import ColumnReader, TableColumnUsage
from databuilder.serializers import neo4_serializer, neptune_serializer
from databuilder.serializers.neptune_serializer import (
    NEPTUNE_CREATION_TYPE_JOB, NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_HEADER_ID,
    NEPTUNE_HEADER_LABEL, NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT,
    NEPTUNE_RELATIONSHIP_HEADER_FROM, NEPTUNE_RELATIONSHIP_HEADER_TO,
)


class TestTableColumnUsage(unittest.TestCase):

    def setUp(self) -> None:
        col_readers = [
            ColumnReader(
                database='db',
                cluster='gold',
                schema='scm',
                table='foo',
                column='*',
                user_email='john@example.com'
            )
        ]
        self.table_col_usage = TableColumnUsage(col_readers=col_readers)

    @no_type_check  # mypy is somehow complaining on assignment on expected dict.
    def test_serialize(self) -> None:
        node_row = self.table_col_usage.next_node()
        actual = []
        while node_row:
            actual.append(neo4_serializer.serialize_node(node_row))
            node_row = self.table_col_usage.next_node()

        expected = [{'first_name': '',
                     'last_name': '',
                     'full_name': '',
                     'employee_type': '',
                     'is_active:UNQUOTED': True,
                     'updated_at:UNQUOTED': 0,
                     'LABEL': 'User',
                     'slack_id': '',
                     'KEY': 'john@example.com',
                     'github_username': '',
                     'team_name': '',
                     'email': 'john@example.com',
                     'role_name': ''}]
        self.assertEqual(expected, actual)

        rel_row = self.table_col_usage.next_relation()
        actual = []
        while rel_row:
            actual.append(neo4_serializer.serialize_relationship(rel_row))
            rel_row = self.table_col_usage.next_relation()

        expected = [{'read_count:UNQUOTED': 1, 'END_KEY': 'john@example.com', 'START_LABEL': 'Table',
                     'END_LABEL': 'User', 'START_KEY': 'db://gold.scm/foo', 'TYPE': 'READ_BY', 'REVERSE_TYPE': 'READ'}]
        self.assertEqual(expected, actual)

    def test_neptune_serialize(self) -> None:
        rel_row = self.table_col_usage.next_relation()
        actual = []
        while rel_row:
            actual.append(neptune_serializer.convert_relationship(rel_row))
            rel_row = self.table_col_usage.next_relation()
        expected = [[
            {
                NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                    from_vertex_id='db://gold.scm/foo',
                    to_vertex_id='john@example.com',
                    label='READ_BY'
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: 'db://gold.scm/foo',
                NEPTUNE_RELATIONSHIP_HEADER_TO: 'john@example.com',
                NEPTUNE_HEADER_LABEL: 'READ_BY',
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
                'read_count:Long(single)': 1
            },
            {
                NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                    from_vertex_id='john@example.com',
                    to_vertex_id='db://gold.scm/foo',
                    label='READ'
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: 'john@example.com',
                NEPTUNE_RELATIONSHIP_HEADER_TO: 'db://gold.scm/foo',
                NEPTUNE_HEADER_LABEL: 'READ',
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
                'read_count:Long(single)': 1
            }
        ]]
        self.maxDiff = None
        self.assertListEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
