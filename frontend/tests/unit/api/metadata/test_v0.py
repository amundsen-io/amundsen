import json
import responses
import unittest

from http import HTTPStatus

from amundsen_application import create_app

local_app = create_app('amundsen_application.config.LocalConfig')


class MetadataTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_popular_tables = {
            'popular_tables': [
                {
                    'table_name': 'test_table',
                    'schema': 'test_schema',
                    'database': 'test_db',
                    'cluster': 'test_cluster',
                    'table_description': 'This is a test'
                }
            ]
        }
        self.expected_parsed_popular_tables = [
            {
                'name': 'test_table',
                'schema_name': 'test_schema',
                'cluster': 'test_cluster',
                'database': 'test_db',
                'description': 'This is a test',
                'key': 'test_db://test_cluster.test_schema/test_table',
            }
        ]
        self.mock_metadata = {
            'database': 'test_db',
            'cluster': 'test_cluster',
            'schema': 'test_schema',
            'table_name': 'test_table',
            'table_description': 'This is a test',
            'tags': [],
            'table_readers': [
                {'reader': {'email': 'test@test.com', 'first_name': None, 'last_name': None}, 'read_count': 100}
            ],
            'owners': [],
            'columns': [
                {
                    'name': 'column_1',
                    'description': 'This is a test',
                    'type': 'bigint',
                    'sort_order': 0,
                    'stats': [
                        {'stat_type': 'count', 'stat_val': '100', 'start_epoch': 1538352000, 'end_epoch': 1538352000},
                        {'stat_type': 'count_null', 'stat_val': '0', 'start_epoch': 1538352000, 'end_epoch': 1538352000}
                    ]
                }
            ],
            'watermarks': [
                {'watermark_type': 'low_watermark', 'partition_key': 'ds', 'partition_value': '', 'create_time': ''},
                {'watermark_type': 'high_watermark', 'partition_key': 'ds', 'partition_value': '', 'create_time': ''}
            ],
            'table_writer': {
                'application_url': 'https://test-test.test.test',
                'name': 'test_name',
                'id': 'test_id',
                'description': 'This is a test'
            },
            'last_updated_timestamp': 1534191754
        }
        self.expected_parsed_metadata = {
            'cluster': 'test_cluster',
            'database': 'test_db',
            'schema': 'test_schema',
            'table_name': 'test_table',
            'table_description': 'This is a test',
            'tags': [],
            'table_readers': [
                {
                    'reader': {
                        'email': 'test@test.com',
                        'first_name': None,
                        'last_name': None,
                        'display_name': 'test@test.com',
                        'profile_url': ''
                    },
                    'read_count': 100
                }
            ],
            'partition': {
                'is_partitioned': True,
                'key': 'ds',
                'value': '01-30-2019'
            },
            'owners': [],
            'columns': [
                {
                    'name': 'column_1',
                    'description': 'This is a test',
                    'type': 'bigint',
                    'sort_order': 0,
                    'stats': [
                        {'stat_type': 'count', 'stat_val': '100', 'start_epoch': 1538352000, 'end_epoch': 1538352000},
                        {'stat_type': 'count_null', 'stat_val': '0', 'start_epoch': 1538352000, 'end_epoch': 1538352000}
                    ],
                    'is_editable': True
                }
            ],
            'table_writer': {
                'application_url': 'https://test-test.test.test',
                'name': 'test_name',
                'id': 'test_id',
                'description': 'This is a test'
            },
            'watermarks': [
                {'watermark_type': 'low_watermark', 'partition_key': 'ds', 'partition_value': '', 'create_time': ''},
                {'watermark_type': 'high_watermark', 'partition_key': 'ds', 'partition_value': '', 'create_time': ''}
            ],
            'source': '/source',
            'is_editable': True
        }
        self.mock_tags = {
            'tag_usages': [
                {
                    'tag_count': 3,
                    'tag_name': 'tag_0'
                }, {
                    'tag_count': 4,
                    'tag_name': 'tag_1'
                }, {
                    'tag_count': 5,
                    'tag_name': 'tag_2'
                }, {
                    'tag_count': 10,
                    'tag_name': 'tag_3'
                }, {
                    'tag_count': 1,
                    'tag_name': 'tag_4'
                }
            ]
        }
        self.expected_parsed_tags = [
            {
                "tag_count": 3,
                "tag_name": "tag_0"
            },
            {
                "tag_count": 4,
                "tag_name": "tag_1"
            },
            {
                "tag_count": 5,
                "tag_name": "tag_2"
            },
            {
                "tag_count": 10,
                "tag_name": "tag_3"
            },
            {
                "tag_count": 1,
                "tag_name": "tag_4"
            }
        ]

    @responses.activate
    def test_popular_tables_success(self) -> None:
        """
        Test successful popular_tables request
        :return:
        """
        responses.add(responses.GET, local_app.config['METADATASERVICE_POPULAR_TABLES_ENDPOINT'],
                      json=self.mock_popular_tables, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/popular_tables')
            data = json.loads(response.data)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertCountEqual(data.get('results'), self.expected_parsed_popular_tables)

    @responses.activate
    def test_popular_tables_propagate_failure(self) -> None:
        """
        Test that any error codes from the request are propagated through, to be
        returned to the React application
        :return:
        """
        responses.add(responses.GET, local_app.config['METADATASERVICE_POPULAR_TABLES_ENDPOINT'],
                      json=self.mock_popular_tables, status=HTTPStatus.BAD_REQUEST)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/popular_tables')
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @responses.activate
    def test_popular_tables_catch_exception(self) -> None:
        """
        Test catching exception if there is an issue processing the popular table
        results from the metadata service
        :return:
        """
        responses.add(responses.GET, local_app.config['METADATASERVICE_POPULAR_TABLES_ENDPOINT'],
                      json={'popular_tables': None}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/popular_tables')
            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    @responses.activate
    def test_get_table_metadata_success(self) -> None:
        """
        Test successful get_table_metadata request
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] + '/db://cluster.schema/table'
        responses.add(responses.GET, url, json=self.mock_metadata, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/table',
                query_string=dict(
                    db='db',
                    cluster='cluster',
                    schema='schema',
                    table='table',
                    index='0',
                    source='test_source'
                )
            )
            data = json.loads(response.data)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertCountEqual(data.get('tableData'), self.expected_parsed_metadata)

    @responses.activate
    def test_update_table_owner_success(self) -> None:
        """
        Test successful update_table_owner request
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] + '/db://cluster.schema/table/owner/test'
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/update_table_owner',
                json={
                    'db': 'db',
                    'cluster': 'cluster',
                    'schema': 'schema',
                    'table': 'table',
                    'owner': 'test'
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)

    @responses.activate
    def test_get_last_indexed_success(self) -> None:
        """
        Test successful get_last_indexed request
        :return:
        """
        responses.add(responses.GET, local_app.config['METADATASERVICE_LAST_INDEXED_ENDPOINT'],
                      json={'neo4j_latest_timestamp': 1538352000}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/get_last_indexed')
            data = json.loads(response.data)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(data.get('timestamp'), 1538352000)

    @responses.activate
    def test_get_last_indexed_propagate_failure(self) -> None:
        """
        Test that any error codes from the get_last_indexed request are propagated through,
        to be returned to the React application
        :return:
        """
        responses.add(responses.GET, local_app.config['METADATASERVICE_LAST_INDEXED_ENDPOINT'],
                      json=None, status=HTTPStatus.BAD_REQUEST)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/get_last_indexed')
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @responses.activate
    def test_get_table_description_success(self) -> None:
        """
        Test successful get_table_description request
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] + '/db://cluster.schema/table/description'
        responses.add(responses.GET, url, json={'description': 'This is a test'}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/get_table_description',
                query_string=dict(db='db', cluster='cluster', schema='schema', table='table')
            )
            data = json.loads(response.data)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(data.get('description'), 'This is a test')

    @responses.activate
    def test_get_table_description_propagate_failure(self) -> None:
        """
        Test that any error codes from the get_table_description request are propagated through,
        to be returned to the React application
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] + '/db://cluster.schema/table/description'
        responses.add(responses.GET, url, json={'description': 'This is a test'}, status=HTTPStatus.BAD_REQUEST)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/get_table_description',
                query_string=dict(db='db', cluster='cluster', schema='schema', table='table')
            )
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @responses.activate
    def test_put_table_description_success(self) -> None:
        """
        Test successful put_table_description request
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] + '/db://cluster.schema/table/description/test'
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/put_table_description',
                json={
                    'db': 'db',
                    'cluster': 'cluster',
                    'schema': 'schema',
                    'table': 'table',
                    'description': 'test',
                    'source': 'source'
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)

    @responses.activate
    def test_get_column_description_success(self) -> None:
        """
        Test successful get_column_description request
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] + '/db://cluster.schema/table/column/colA/description'
        responses.add(responses.GET, url, json={'description': 'This is a test'}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/get_column_description',
                query_string=dict(
                    db='db',
                    cluster='cluster',
                    schema='schema',
                    table='table',
                    index='0',
                    column_name='colA'
                )
            )
            data = json.loads(response.data)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(data.get('description'), 'This is a test')

    @responses.activate
    def test_get_column_description_propagate_failure(self) -> None:
        """
        Test that any error codes from the get_column_description request are propagated through,
        to be returned to the React application
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] + '/db://cluster.schema/table/column/colA/description'
        responses.add(responses.GET, url, json={'description': 'This is a test'}, status=HTTPStatus.BAD_REQUEST)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/get_column_description',
                query_string=dict(
                    db='db',
                    cluster='cluster',
                    schema='schema',
                    table='table',
                    index='0',
                    column_name='colA'
                )
            )
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @responses.activate
    def test_put_column_description_success(self) -> None:
        """
        Test successful put_column_description request
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] \
            + '/db://cluster.schema/table/column/col/description/test'
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/put_column_description',
                json={
                    'db': 'db',
                    'cluster': 'cluster',
                    'schema': 'schema',
                    'table': 'table',
                    'column_name': 'col',
                    'description': 'test',
                    'source': 'source'
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)

    @responses.activate
    def test_get_tags(self) -> None:
        """
        Test successful fetch of all tags
        :return:
        """
        url = local_app.config['METADATASERVICE_TAGS_ENDPOINT']
        responses.add(responses.GET, url, json=self.mock_tags, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/tags')
            data = json.loads(response.data)
            self.assertCountEqual(data.get('tags'), self.expected_parsed_tags)

    @responses.activate
    def test_update_table_tags_put(self) -> None:
        """
        Test adding a tag on a table
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] + '/db://cluster.schema/table/tag/tag_5'
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/update_table_tags',
                json={
                    'db': 'db',
                    'cluster': 'cluster',
                    'schema': 'schema',
                    'table': 'table',
                    'tag': 'tag_5'
                }
            )
            self.assertEquals(response.status_code, HTTPStatus.OK)

    @responses.activate
    def test_update_table_tags_delete(self) -> None:
        """
        Test deleting a tag on a table
        :return:
        """
        url = local_app.config['METADATASERVICE_TABLE_ENDPOINT'] + '/db://cluster.schema/table/tag/tag_5'
        responses.add(responses.DELETE, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.delete(
                '/api/metadata/update_table_tags',
                json={
                    'db': 'db',
                    'cluster': 'cluster',
                    'schema': 'schema',
                    'table': 'table',
                    'tag': 'tag_5'
                }
            )
            self.assertEquals(response.status_code, HTTPStatus.OK)
