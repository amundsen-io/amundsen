import string
import unittest

from mock import MagicMock, patch
from typing import List, Callable, Tuple

from search_service import create_app, config
from search_service.models.search_result import SearchResult
from search_service.models.table import Table
from search_service.proxy import get_proxy_client


class TestAtlasProxy(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.app = create_app(config_module_class='search_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.qn = False
        with self.app_context:
            from search_service.proxy.atlas import AtlasProxy
            self.proxy = AtlasProxy(host='DOES_NOT_MATTER:0000')
            self.proxy.atlas = MagicMock()
            self.qn = self.app.config['ATLAS_NAME_ATTRIBUTE'] == "qualifiedName"
        self.entity_type = 'TEST_ENTITY'
        self.cluster = 'TEST_CLUSTER'
        self.db = 'TEST_DB'
        self.name = 'TEST_TABLE'
        self.table_uri = f'{self.entity_type}://{self.cluster}.{self.db}/{self.name}'

        self.classification_entity = {
            'classifications': [
                {'typeName': 'PII_DATA', 'name': 'PII_DATA'},
            ]
        }
        self.test_column = {
            'guid': 'DOESNT_MATTER',
            'typeName': 'COLUMN',
            'attributes': {
                'qualifiedName': f"{self.db}.Table1.column@{self.cluster}",
                'type': 'Managed',
                'description': 'column description',
                'position': 1
            }

        }
        self.db_entity = {
            'guid': '-100',
            'typeName': self.entity_type,
            'attributes': {
                'qualifiedName': self.db + "@" + self.cluster,
                'name': self.db,
                'clusterName': self.cluster
            }
        }
        self.entity1 = {
            'guid': '1',
            'typeName': self.entity_type,
            'classificationNames': [
                'PII_DATA'
            ],
            'relationshipAttributes': {
                'db': self.db_entity
            },
            'attributes': {
                'updateTime': 123,
                'name': 'Table1',
                'qualifiedName': f"{self.db}.Table1@{self.cluster}",
                'classifications': [
                    {'typeName': 'PII_DATA'}
                ],
                'description': 'Dummy Description',
                'owner': 'dummy@email.com',
                'columns': [self.test_column],
                'db': self.db_entity
            }
        }
        self.entity1.update(self.classification_entity)

        self.entity2 = {
            'guid': '2',
            'typeName': self.entity_type,
            'classificationNames': [],
            'attributes': {
                'updateTime': 234,
                'qualifiedName': f"Table2",
                'name': 'Table2',
                'db': None,
                'description': 'Dummy Description',
                'owner': 'dummy@email.com',
            }
        }
        self.entity2.update(self.classification_entity)
        self.entities = {
            'entities': [
                self.entity1,
                self.entity2,
            ],
        }

    def _qualified(self, kind, name, table=None):
        if not self.qn:
            return name
        if kind == "db":
            return f"{name}@{self.cluster}"
        if kind == "column" and table:
            return f"{self.db}.{table}.{name}@{self.cluster}"
        if kind == "table":
            return f"{self.db}.{name}@{self.cluster}"
        return name

    @staticmethod
    def recursive_mock(start: any):
        """
        The atlas client allows retrieval of data via __getattr__.
        That is why we build this method to recursively mock dictionary's to add
        the __getattr__ and to convert them into MagicMock.
        :param start: dictionary, list, or other
        :return: MagicMock, list with mocked items, or other
        """
        if isinstance(start, dict):
            dict_mock = MagicMock()
            dict_mock.__getitem__.side_effect = start.__getitem__
            dict_mock.__iter__.side_effect = start.__iter__
            dict_mock.__contains__.side_effect = start.__contains__
            dict_mock.get.side_effect = start.get
            for key, value in start.items():
                value_mock = TestAtlasProxy.recursive_mock(value)
                dict_mock.__setattr__(key, value_mock)
                start[key] = value_mock
            return dict_mock
        elif isinstance(start, (list,)):
            return list(map(TestAtlasProxy.recursive_mock, start))
        else:
            return start

    @staticmethod
    def dsl_inject(checks: List[Tuple[Callable[[str], bool], dict]]):
        """
        helper method for returning results based on sql queries
        :param checks:
        :return:
        """
        def search_dsl(query: string):
            for check, data in checks:
                if check(query):
                    response = MagicMock()
                    d = TestAtlasProxy.recursive_mock(data)
                    d.__iter__.return_value = [d]
                    d._data = {
                        'queryType': "DSL",
                        'queryText': query,
                        **data
                    }
                    response.__iter__.return_value = [d]

                    return response
            raise Exception(f"query not supported: {query}")

        return search_dsl

    @staticmethod
    def bulk_inject(entities: dict):
        """
        provide an entity_bulk method for atlas
        :param entities:
        :return:
        """
        # noinspection PyPep8Naming
        def guid_filter(guid: List, ignoreRelationships=False):
            return TestAtlasProxy.recursive_mock([{
                'entities': list(filter(lambda x: x['guid'] in guid, entities))
            }])

        return guid_filter

    def test_setup_client(self) -> None:
        with self.app_context:
            from search_service.proxy.atlas import AtlasProxy
            client = AtlasProxy(
                host="http://localhost:21000",
                user="admin",
                password="admin",
                page_size=1337
            )
            self.assertEqual(client.atlas.base_url, "http://localhost:21000")
            self.assertEqual(client.atlas.client.request_params['headers']['Authorization'], 'Basic YWRtaW46YWRtaW4=')
            self.assertEqual(client.page_size, 1337)

    @patch('search_service.proxy._proxy_client', None)
    def test_setup_config(self) -> None:
        # Gather all the configuration to create a Proxy Client
        self.app.config[config.PROXY_ENDPOINT] = "http://localhost:21000"
        self.app.config[config.PROXY_USER] = "admin"
        self.app.config[config.PROXY_PASSWORD] = "admin"
        self.app.config[config.PROXY_CLIENT] = config.PROXY_CLIENTS['ATLAS']
        self.app.config[config.SEARCH_PAGE_SIZE_KEY] = 1337

        client = get_proxy_client()
        self.assertEqual(client.atlas.base_url, "http://localhost:21000")
        self.assertEqual(client.atlas.client.request_params['headers']['Authorization'], 'Basic YWRtaW46YWRtaW4=')
        self.assertEqual(client.page_size, 1337)

    def test_search_normal(self):
        expected = SearchResult(total_results=2,
                                results=[Table(name=self.entity1['attributes']['name'],
                                               key=f"{self.entity_type}://"
                                                   f"{self.cluster}.{self.db}/"
                                                   f"{self.entity1['attributes']['name']}",
                                               description=self.entity1['attributes']['description'],
                                               cluster=self.cluster,
                                               database=self.entity_type,
                                               schema_name=self.db,
                                               column_names=[],
                                               tags=['PII_DATA'],
                                               last_updated_epoch=123),
                                         Table(name='Table2',
                                               key=f"TEST_ENTITY://default.default/Table2",
                                               description='Dummy Description',
                                               cluster='default',
                                               database=self.entity_type,
                                               schema_name='default',
                                               column_names=[],
                                               tags=[],
                                               last_updated_epoch=234)])
        self.proxy.atlas.search_dsl = self.dsl_inject(
            [
                (lambda dsl: "select count()" in dsl and "Table" in dsl,
                 {"attributes": {"name": ["count()"], "values": [[2]]}}),
                (lambda dsl: "Table" in dsl and any(x in dsl for x in ["select table", "from Table"]),
                 {'entities': [self.entity1, self.entity2]})
            ]
        )
        self.proxy.atlas.entity_bulk = self.bulk_inject([
            self.entity1,
            self.entity2,
            self.db_entity
        ])
        resp = self.proxy.fetch_table_search_results(query_term="Table")
        self.assertTrue(resp.total_results == 2, "there should be 2 search result")
        self.assertIsInstance(resp.results[0], Table, "Search result received is not of 'Table' type!")
        self.assertDictEqual(vars(resp.results[0]), vars(expected.results[0]),
                             "Search Result doesn't match with expected result!")
        self.assertDictEqual(vars(resp.results[1]), vars(expected.results[1]),
                             "Search Result doesn't match with expected result!")

    def test_search_empty(self):
        expected = SearchResult(total_results=0,
                                results=[])
        self.proxy.atlas.search_dsl = self.dsl_inject([
            (lambda dsl: "select count()" in dsl,
             {"attributes": {"name": ["count()"], "values": [[0]]}}),
            (lambda dsl: any(x in dsl for x in ["select table", "from Table"]),
             {'entities': []})
        ])
        self.proxy.atlas.entity_bulk = self.bulk_inject([
            self.entity1,
            self.entity2,
            self.db_entity
        ])
        resp = self.proxy.fetch_table_search_results(query_term="Table1")
        self.assertTrue(resp.total_results == 0, "there should no search results")
        self.assertIsInstance(resp, SearchResult, "Search result received is not of 'SearchResult' type!")
        self.assertDictEqual(vars(resp), vars(expected),
                             "Search Result doesn't match with expected result!")

    def test_search_fields(self):
        fields = ['tag', 'schema', 'table', 'column']
        for field in fields:

            expected = SearchResult(total_results=1,
                                    results=[Table(name=self.entity1['attributes']['name'],
                                                   key=f"{self.entity_type}://"
                                                       f"{self.cluster}.{self.db}/"
                                                       f"{self.entity1['attributes']['name']}",
                                                   description=self.entity1['attributes']['description'],
                                                   cluster=self.cluster,
                                                   database=self.entity_type,
                                                   schema_name=self.db,
                                                   column_names=[],
                                                   tags=['PII_DATA'],
                                                   last_updated_epoch=123)])
            self.proxy.atlas.search_dsl = self.dsl_inject(
                [
                    (lambda dsl: "select count()" in dsl,
                     {"attributes": {"name": ["count()"], "values": [[1]]}}),
                    (lambda dsl: any(x in dsl for x in ["select table", "from Table", "hive_column"]),
                     {'entities': [self.entity1]})
                ]
            )
            self.proxy.atlas.entity_bulk = self.bulk_inject([
                self.entity1,
                self.db_entity
            ])
            resp = self.proxy.fetch_table_search_results_with_field(
                query_term=field + "Table1",
                field_name=field,
                field_value="Table1"
            )
            self.assertTrue(resp.total_results == 1, "there should be 1 search result")
            self.assertIsInstance(resp.results[0], Table, "Search result received is not of 'Table' type!")
            self.assertDictEqual(vars(resp.results[0]), vars(expected.results[0]),
                                 "Search Result doesn't match with expected result!")

    def test_unknown_field(self):
        expected = SearchResult(total_results=0,
                                results=[])
        self.proxy.atlas.search_dsl = self.dsl_inject([
            (lambda dsl: "select count()" in dsl,
             {"attributes": {"name": ["count()"], "values": [[0]]}}),
            (lambda dsl: any(x in dsl for x in ["select table", "from Table"]),
             {'entities': []})
        ])
        self.proxy.atlas.entity_bulk = self.bulk_inject([
            self.entity1,
            self.entity2,
            self.db_entity
        ])
        resp = self.proxy.fetch_table_search_results(query_term="unknown:Table1")
        self.assertTrue(resp.total_results == 0, "there should no search results")
        self.assertIsInstance(resp, SearchResult, "Search result received is not of 'SearchResult' type!")
        self.assertDictEqual(vars(resp), vars(expected),
                             "Search Result doesn't match with expected result!")
