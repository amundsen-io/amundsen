# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import unittest


from databuilder.databuilder.utils.nested_column_parser import get_columns_from_type


class TestNestedColumnParser(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.base_column_name = 'base_column'

    def test_parse_scalar(self) -> None:
        col_type = 'string'
        expected = [{
            'col_type': 'string',
            'name': 'base_column',
            'full_name': 'base_column',
        }]
        actual = get_columns_from_type(self.base_column_name, col_type)
        self.assertEqual(actual, expected)

    def test_parse_simple_array(self) -> None:
        col_type = 'array<string>'
        expected = [{
            'col_type': 'array<string>',
            'name': 'base_column',
            'full_name': 'base_column',
        }]
        actual = get_columns_from_type(self.base_column_name, col_type)
        self.assertEqual(actual, expected)

     def test_parse_simple_struct(self) -> None:
        col_type = 'struct<col_1:string, col_2:string>'
        expected = [
                       {
                           'col_type': 'struct<col_1:string, col_2:string>',
                           'name': 'base_column',
                           'full_name': 'base_column',
                       },
                       {
                           'col_type': 'string',
                           'name': 'col_1',
                           'full_name': 'base_column.col_1',
                       },
                       {
                           'col_type': 'string',
                           'name': 'col_2',
                           'full_name': 'base_column.col_2',
                       },
                   ]
        actual = get_columns_from_type(self.base_column_name, col_type)
        self.assertEqual(actual, expected)


    def test_parse_nested_struct(self) -> None:
        col_type = 'struct<col_1:string,col_2:struct<col_3:boolean,col_4:timestamp>>'
        expected =  [
                        {
                            'name': 'base_column',
                            'full_name': 'base_column',
                            'col_type': 'struct<col_1:string,col_2:struct<col_3:boolean,col_4:timestamp>>'
                        },
                        {
                            'name': 'col_1',
                            'full_name': 'base_column.col_1',
                            'col_type': 'string'
                        },
                        {
                            'name': 'col_2',
                            'full_name': 'base_column.col_2',
                            'col_type': 'struct<col_3:boolean,col_4:timestamp>'
                        },
                        {
                            'name': 'col_3',
                            'full_name': 'base_column.col_2.col_3',
                            'col_type': 'boolean'
                        },
                        {
                            'name': 'col_4',
                            'full_name': 'base_column.col_2.col_4',
                            'col_type': 'timestamp'
                        }
                    ],
        actual = get_columns_from_type(self.base_column_name, col_type)
        self.assertEqual(actual, expected)


    def test_parse_array_nested_struct(self) -> None:
        col_type =  'array<struct<col_1:string, col_2:int>>'
        expected =  [
                        {
                            'name': 'base_column',
                            'full_name': 'base_column',
                            'col_type': 'array<struct<col_1:string, col_2:int>>',
                        },
                        {
                            'name': 'col_1',
                            'full_name': 'base_column.col_1',
                            'col_type': 'string'
                        },
                        {
                            'name': 'col_2',
                            'full_name': 'base_column.col_2',
                            'col_type': 'int'
                        },
                    ],
        actual = get_columns_from_type(self.base_column_name, col_type)
        self.assertEqual(actual, expected)

    def test_parse_row(self) -> None:
        col_type =  'row(col_1:varchar, col_2:int, col_3:array(int))',
        expected =  [
                        {
                            'name': 'base_column',
                            'full_name': 'base_column',
                            'col_type': 'row(col_1:varchar, col_2:int, col_3:array(int))',
                        },
                        {
                            'name': 'col_1',
                            'full_name': 'base_column.col_1',
                            'col_type': 'varchar'
                        },
                        {
                            'name': 'col_2',
                            'full_name': 'base_column.col_2',
                            'col_type': 'int'
                        },
                        {
                            'name': 'col_3',
                            'full_name': 'base_column.col_3',
                            'col_type': 'array(int)'
                        },
                    ],
        actual = get_columns_from_type(self.base_column_name, col_type)
        self.assertEqual(actual, expected)
