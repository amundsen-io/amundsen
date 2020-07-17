# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from unittest.mock import patch, Mock

from amundsen_application.api.utils.metadata_utils import _update_prog_descriptions, _sort_prog_descriptions, \
    _parse_editable_rule
from amundsen_application.config import MatchRuleObject
from amundsen_application import create_app

local_app = create_app('amundsen_application.config.TestConfig', 'tests/templates')


class ProgrammaticDescriptionsTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    @patch('amundsen_application.api.utils.metadata_utils._sort_prog_descriptions')
    def test_update_prog_descriptions(self, sort_mock) -> None:
        with local_app.app_context():
            test_desc = [
                {'source': 'c_1', 'text': 'description c'},
                {'source': 'a_1', 'text': 'description a'},
                {'source': 'b_1', 'text': 'description b'}
            ]
            # Pretend config exists
            local_app.config['PROGRAMMATIC_DISPLAY'] = Mock()
            # Mock the effects of the sort method
            sort_mock.side_effect = [1, 0, 1]
            # Expected order based on mocked side effect
            expected_programmatic_desc = [
                {'source': 'a_1', 'text': 'description a'},
                {'source': 'c_1', 'text': 'description c'},
                {'source': 'b_1', 'text': 'description b'}
            ]
            _update_prog_descriptions(test_desc)
            self.assertEqual(test_desc, expected_programmatic_desc)

    def test_sort_prog_descriptions_returns_value_from_config(self) -> None:
        """
        Verify the method will return the display order from the programmtic description
        configuration if it exists for the given source
        :return:
        """
        with local_app.app_context():
            mock_order = 1
            mock_config = {
                "c_1": {
                    "display_order": mock_order
                }
            }
            in_config_value = {'source': 'c_1', 'text': 'I am a test'}
            self.assertEqual(_sort_prog_descriptions(mock_config, in_config_value), mock_order)

    def test_sort_prog_descriptions_returns_default_value(self) -> None:
        """
        Verify the method will return the expected default value if programmtic decsription
        source is not included in teh configuration
        :return:
        """
        with local_app.app_context():
            mock_config = {
                "c_1": {
                    "display_order": 0
                }
            }
            not_in_config_value = {'source': 'test', 'text': 'I am a test'}
            self.assertEqual(_sort_prog_descriptions(mock_config, not_in_config_value), len(mock_config))


class UneditableTableDescriptionTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_table_desc_match_rule_schema_only(self) -> None:
        # Mock match rule, table name and schema
        test_match_rule = MatchRuleObject(schema_regex=r"^(schema1)")

        # assert result for given schema and match rule
        self.assertEqual(_parse_editable_rule(test_match_rule, 'schema1', 'test_table'), False)
        self.assertEqual(_parse_editable_rule(test_match_rule, 'schema2', 'test_table'), True)

    def test_table_desc_match_rule_table_only(self) -> None:
        # Mock match rule, table name and schema
        test_match_rule = MatchRuleObject(table_name_regex=r"^noedit_([a-zA-Z_0-9]+)")

        # assert result for given table name and match rule
        self.assertEqual(_parse_editable_rule(test_match_rule, 'schema', 'noedit_test_table'), False)
        self.assertEqual(_parse_editable_rule(test_match_rule, 'schema', 'editable_test_table'), True)

    def test_table_desc_match_rule_schema_and_table(self) -> None:
        # Mock match rule, table name and schema
        test_match_rule = MatchRuleObject(schema_regex=r"^(schema1|schema2)",
                                          table_name_regex=r"^other_([a-zA-Z_0-9]+)")
        # assert result for given schema, table name and match rule
        self.assertEqual(_parse_editable_rule(test_match_rule, 'schema1', 'other_test_table'), False)
        self.assertEqual(_parse_editable_rule(test_match_rule, 'schema1', 'test_table'), True)
        self.assertEqual(_parse_editable_rule(test_match_rule, 'schema3', 'other_test_table'), True)
        self.assertEqual(_parse_editable_rule(test_match_rule, 'schema3', 'test_table'), True)
