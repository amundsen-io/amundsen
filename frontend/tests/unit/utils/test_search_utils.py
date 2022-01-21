# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from amundsen_application.api.utils.search_utils import generate_query_json


class SearchUtilsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test_filters = {
            'invalid_option': {'value': 'invalid'},
            'column': {'value': 'column_name'},
            'database': {'value': 'db1, db3'},
            'schema': {'value': 'schema_name'},
            'table': {'value': 'table_name'},
            'tag': {'value': 'tag_name'},
        }
        self.expected_transformed_filters = {
            'column': ['column_name'],
            'database': ['db1', 'db3'],
            'schema': ['schema_name'],
            'table': ['table_name'],
            'tag': ['tag_name'],
        }
        self.test_page_index = 1
        self.test_term = 'hello'

    def test_generate_query_json(self) -> None:
        """
        Verify that the returned diction correctly transforms the parameters
        :return:
        """
        query_json = generate_query_json(filters=self.expected_transformed_filters,
                                         page_index=self.test_page_index,
                                         search_term=self.test_term)
        self.assertEqual(query_json.get('page_index'), int(self.test_page_index))
        self.assertEqual(query_json.get('search_request'), {
            'type': 'AND',
            'filters': self.expected_transformed_filters
        })
        self.assertEqual(query_json.get('query_term'), self.test_term)
