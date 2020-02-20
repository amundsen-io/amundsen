import unittest

from mock import patch

from databuilder.rest_api.base_rest_api_query import RestApiQuerySeed
from databuilder.rest_api.rest_api_query import RestApiQuery


class TestRestApiQuery(unittest.TestCase):

    def test_rest_api_query_seed(self):
        rest_api_query = RestApiQuerySeed(seed_record=[
            {'foo': 'bar'},
            {'john': 'doe'}
        ])

        result = [v for v in rest_api_query.execute()]
        expected = [
            {'foo': 'bar'},
            {'john': 'doe'}
        ]

        self.assertListEqual(expected, result)

    def test_rest_api_query(self):

        seed_record = [{'foo1': 'bar1'},
                       {'foo2': 'bar2'}]
        seed_query = RestApiQuerySeed(seed_record=seed_record)

        with patch('databuilder.rest_api.rest_api_query.requests.get') as mock_get:
            json_path = 'foo.name'
            field_names = ['name_field']

            mock_get.return_value.json.side_effect = [
                {'foo': {'name': 'john'}},
                {'foo': {'name': 'doe'}},
            ]
            query = RestApiQuery(query_to_join=seed_query, url='foobar', params={},
                                 json_path=json_path, field_names=field_names)

            expected = [
                {'name_field': 'john', 'foo1': 'bar1'},
                {'name_field': 'doe', 'foo2': 'bar2'}
            ]

            for actual in query.execute():
                self.assertDictEqual(expected.pop(0), actual)

    def test_rest_api_query_multiple_fields(self):

        seed_record = [{'foo1': 'bar1'},
                       {'foo2': 'bar2'}]
        seed_query = RestApiQuerySeed(seed_record=seed_record)

        with patch('databuilder.rest_api.rest_api_query.requests.get') as mock_get:
            json_path = 'foo.[name,hobby]'
            field_names = ['name_field', 'hobby']

            mock_get.return_value.json.side_effect = [
                {'foo': {'name': 'john', 'hobby': 'skiing'}},
                {'foo': {'name': 'doe', 'hobby': 'snowboarding'}},
            ]
            query = RestApiQuery(query_to_join=seed_query, url='foobar', params={},
                                 json_path=json_path, field_names=field_names)

            expected = [
                {'name_field': 'john', 'hobby': 'skiing', 'foo1': 'bar1'},
                {'name_field': 'doe', 'hobby': 'snowboarding', 'foo2': 'bar2'}
            ]

            for actual in query.execute():
                self.assertDictEqual(expected.pop(0), actual)
