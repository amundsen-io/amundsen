import json
import responses
import unittest

from http import HTTPStatus

from amundsen_application import create_app
from amundsen_application.api.metadata.v0 import \
    TABLE_ENDPOINT, LAST_INDEXED_ENDPOINT, POPULAR_TABLES_ENDPOINT, TAGS_ENDPOINT, USER_ENDPOINT

from amundsen_application.tests.test_utils import TEST_USER_ID

local_app = create_app('amundsen_application.config.TestConfig', 'tests/templates')


class MetadataTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_popular_tables = {
            'popular_tables': [
                {
                    'cluster': 'test_cluster',
                    'database': 'test_db',
                    'key': 'test_db://test_cluster.test_schema/test_table',
                    'schema': 'test_schema',
                    'table_description': 'This is a test',
                    'table_name': 'test_table',
                    'type': 'table',
                }
            ]
        }
        self.expected_parsed_popular_tables = [
            {
                'cluster': 'test_cluster',
                'database': 'test_db',
                'description': 'This is a test',
                'key': 'test_db://test_cluster.test_schema/test_table',
                'schema_name': 'test_schema',
                'type': 'table',
                'name': 'test_table',
                'last_updated_epoch': None,
            }
        ]
        self.mock_metadata = {
            'cluster': 'test_cluster',
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
            'database': 'test_db',
            'is_view': False,
            'key': 'test_db://test_cluster.test_schema/test_table',
            'owners': [],
            'schema': 'test_schema',
            'table_name': 'test_table',
            'table_description': 'This is a test',
            'tags': [],
            'table_readers': [
                {'reader': {'email': 'test@test.com', 'first_name': None, 'last_name': None}, 'read_count': 100}
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
        }
        self.expected_parsed_metadata = {
            'key': 'table_key',
            'badges': [],
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
            'is_view': False,
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
                'tag_count': 3,
                'tag_name': 'tag_0'
            },
            {
                'tag_count': 4,
                'tag_name': 'tag_1'
            },
            {
                'tag_count': 5,
                'tag_name': 'tag_2'
            },
            {
                'tag_count': 10,
                'tag_name': 'tag_3'
            },
            {
                'tag_count': 1,
                'tag_name': 'tag_4'
            }
        ]
        self.mock_user = {
            'email': 'test@test.com',
            'employee_type': 'FTE',
            'first_name': 'Firstname',
            'full_name': 'Firstname Lastname',
            'github_username': 'githubusername',
            'is_active': True,
            'last_name': 'Lastname',
            'manager_fullname': 'Manager Fullname',
            'role_name': 'SWE',
            'slack_id': 'slackuserid',
            'team_name': 'Amundsen',
            'user_id': 'testuserid',
        }
        self.expected_parsed_user = {
            'display_name': 'Firstname Lastname',
            'email': 'test@test.com',
            'employee_type': 'FTE',
            'first_name': 'Firstname',
            'full_name': 'Firstname Lastname',
            'github_username': 'githubusername',
            'is_active': True,
            'last_name': 'Lastname',
            'manager_email': 'manager@email.com',
            'manager_fullname': 'Manager Fullname',
            'profile_url': 'https://test-profile-url.com',
            'role_name': 'SWE',
            'slack_id': 'slackuserid',
            'team_name': 'Amundsen',
            'user_id': 'testuserid',
        }
        self.get_user_resource_response = {
            'table': [
                {
                    'cluster': 'cluster',
                    'database': 'database',
                    'schema': 'schema',
                    'table_name': 'table_name_0',
                    'table_description': 'description',
                },
                {
                    'cluster': 'cluster',
                    'database': 'database',
                    'schema': 'schema',
                    'table_name': 'table_name_1',
                    'table_description': 'description',
                },
            ]
        }
        self.expected_parsed_user_resources = [
            {
                'cluster': 'cluster',
                'database': 'database',
                'description': 'description',
                'key': 'database://cluster.schema/table_name_0',
                'last_updated_epoch': None,
                'name': 'table_name_0',
                'schema_name': 'schema',
                'type': 'table',
            },
            {
                'cluster': 'cluster',
                'database': 'database',
                'description': 'description',
                'key': 'database://cluster.schema/table_name_1',
                'last_updated_epoch': None,
                'name': 'table_name_1',
                'schema_name': 'schema',
                'type': 'table',
            },
        ]

    @responses.activate
    def test_popular_tables_success(self) -> None:
        """
        Test successful popular_tables request
        :return:
        """
        responses.add(responses.GET, local_app.config['METADATASERVICE_BASE'] + POPULAR_TABLES_ENDPOINT,
                      json=self.mock_popular_tables, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/popular_tables')
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
        responses.add(responses.GET, local_app.config['METADATASERVICE_BASE'] + POPULAR_TABLES_ENDPOINT,
                      json=self.mock_popular_tables, status=HTTPStatus.BAD_REQUEST)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/popular_tables')
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @responses.activate
    def test_popular_tables_catch_exception(self) -> None:
        """
        Test catching exception if there is an issue processing the popular table
        results from the metadata service
        :return:
        """
        responses.add(responses.GET, local_app.config['METADATASERVICE_BASE'] + POPULAR_TABLES_ENDPOINT,
                      json={'popular_tables': None}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/popular_tables')
            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    @responses.activate
    def test_get_table_metadata_success(self) -> None:
        """
        Test successful get_table_metadata request
        :return:
        """
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + '/db://cluster.schema/table'
        responses.add(responses.GET, url, json=self.mock_metadata, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/v0/table',
                query_string=dict(
                    key='db://cluster.schema/table',
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
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + '/db://cluster.schema/table/owner/test'
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/v0/update_table_owner',
                json={
                    'key': 'db://cluster.schema/table',
                    'owner': 'test'
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)

    @responses.activate
    def test_update_table_owner_propagate_failure(self) -> None:
        """
        Test that any error codes from the update_table_owner request are propagated
        to be returned to the React application
        :return:
        """
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + '/db://cluster.schema/table/owner/test'
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.BAD_REQUEST)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/v0/update_table_owner',
                json={
                    'key': 'db://cluster.schema/table',
                    'owner': 'test'
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @responses.activate
    def test_get_last_indexed_success(self) -> None:
        """
        Test successful get_last_indexed request
        :return:
        """
        responses.add(responses.GET, local_app.config['METADATASERVICE_BASE'] + LAST_INDEXED_ENDPOINT,
                      json={'neo4j_latest_timestamp': 1538352000}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/get_last_indexed')
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
        responses.add(responses.GET, local_app.config['METADATASERVICE_BASE'] + LAST_INDEXED_ENDPOINT,
                      json=None, status=HTTPStatus.BAD_REQUEST)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/get_last_indexed')
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @responses.activate
    def test_get_table_description_success(self) -> None:
        """
        Test successful get_table_description request
        :return:
        """
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + '/db://cluster.schema/table/description'
        responses.add(responses.GET, url, json={'description': 'This is a test'}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/v0/get_table_description',
                query_string=dict(key='db://cluster.schema/table')
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
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + '/db://cluster.schema/table/description'
        responses.add(responses.GET, url, json={'description': 'This is a test'}, status=HTTPStatus.BAD_REQUEST)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/v0/get_table_description',
                query_string=dict(key='db://cluster.schema/table')
            )
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @responses.activate
    def test_put_table_description_success(self) -> None:
        """
        Test successful put_table_description request
        :return:
        """
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + '/db://cluster.schema/table/description'
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/v0/put_table_description',
                json={
                    'key': 'db://cluster.schema/table',
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
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + \
            '/db://cluster.schema/table/column/colA/description'
        responses.add(responses.GET, url, json={'description': 'This is a test'}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/v0/get_column_description',
                query_string=dict(
                    key='db://cluster.schema/table',
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
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + \
            '/db://cluster.schema/table/column/colA/description'
        responses.add(responses.GET, url, json={'description': 'This is a test'}, status=HTTPStatus.BAD_REQUEST)

        with local_app.test_client() as test:
            response = test.get(
                '/api/metadata/v0/get_column_description',
                query_string=dict(
                    key='db://cluster.schema/table',
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
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + \
            '/db://cluster.schema/table/column/col/description'
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/v0/put_column_description',
                json={
                    'key': 'db://cluster.schema/table',
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
        url = local_app.config['METADATASERVICE_BASE'] + TAGS_ENDPOINT
        responses.add(responses.GET, url, json=self.mock_tags, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/tags')
            data = json.loads(response.data)
            self.assertCountEqual(data.get('tags'), self.expected_parsed_tags)

    @responses.activate
    def test_update_table_tags_put(self) -> None:
        """
        Test adding a tag on a table
        :return:
        """
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + '/db://cluster.schema/table/tag/tag_5'
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/v0/update_table_tags',
                json={
                    'key': 'db://cluster.schema/table',
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
        url = local_app.config['METADATASERVICE_BASE'] + TABLE_ENDPOINT + '/db://cluster.schema/table/tag/tag_5'
        responses.add(responses.DELETE, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.delete(
                '/api/metadata/v0/update_table_tags',
                json={
                    'key': 'db://cluster.schema/table',
                    'tag': 'tag_5'
                }
            )
            self.assertEquals(response.status_code, HTTPStatus.OK)

    @responses.activate
    def test_get_user_failure(self) -> None:
        """
        Test get_user fails when no user_id is specified
        """
        url = local_app.config['METADATASERVICE_BASE'] + USER_ENDPOINT + '/testuser'
        responses.add(responses.GET, url, json=self.mock_user, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/user')
            self.assertEquals(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    @responses.activate
    def test_get_user_success(self) -> None:
        """
        Test get_user success
        """
        url = local_app.config['METADATASERVICE_BASE'] + USER_ENDPOINT + '/testuser'
        responses.add(responses.GET, url, json=self.mock_user, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/user', query_string=dict(user_id='testuser'))
            data = json.loads(response.data)
            self.assertEquals(response.status_code, HTTPStatus.OK)
            self.assertCountEqual(data.get('user'), self.expected_parsed_user)

    @responses.activate
    def test_get_bookmark(self) -> None:
        """
        Test get_bookmark with no user specified
        """
        url = '{0}{1}/{2}/follow/'.format(local_app.config['METADATASERVICE_BASE'], USER_ENDPOINT, TEST_USER_ID)
        responses.add(responses.GET, url, json=self.get_user_resource_response, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/user/bookmark')
            data = json.loads(response.data)
            self.assertEquals(response.status_code, HTTPStatus.OK)
            self.assertCountEqual(data.get('bookmarks'), self.expected_parsed_user_resources)

    @responses.activate
    def test_get_bookmark_for_user(self) -> None:
        """
        Test get_bookmark with a specified user
        """
        specified_user = 'other_user'
        url = '{0}{1}/{2}/follow/'.format(local_app.config['METADATASERVICE_BASE'], USER_ENDPOINT, specified_user)
        responses.add(responses.GET, url, json=self.get_user_resource_response, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/user/bookmark', query_string=dict(user_id=specified_user))
            data = json.loads(response.data)
            self.assertEquals(response.status_code, HTTPStatus.OK)
            self.assertCountEqual(data.get('bookmarks'), self.expected_parsed_user_resources)

    @responses.activate
    def test_put_bookmark(self) -> None:
        """
        Test update_bookmark with a PUT request
        """
        resource_type = 'table'
        key = 'database://cluster.schema/table_name_1'
        url = '{0}{1}/{2}/follow/{3}/{4}'.format(local_app.config['METADATASERVICE_BASE'],
                                                 USER_ENDPOINT,
                                                 TEST_USER_ID,
                                                 resource_type,
                                                 key)
        responses.add(responses.PUT, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.put(
                '/api/metadata/v0/user/bookmark',
                json={
                    'type': resource_type,
                    'key': key,
                })

            self.assertEquals(response.status_code, HTTPStatus.OK)

    @responses.activate
    def test_delete_bookmark(self) -> None:
        """
        Test update_bookmark with a DELETE request
        """
        resource_type = 'table'
        key = 'database://cluster.schema/table_name_1'
        url = '{0}{1}/{2}/follow/{3}/{4}'.format(local_app.config['METADATASERVICE_BASE'],
                                                 USER_ENDPOINT,
                                                 TEST_USER_ID,
                                                 resource_type,
                                                 key)
        responses.add(responses.DELETE, url, json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.delete(
                '/api/metadata/v0/user/bookmark',
                json={
                    'type': resource_type,
                    'key': key,
                })

            self.assertEquals(response.status_code, HTTPStatus.OK)

    @responses.activate
    def test_get_user_read(self) -> None:
        """
        Test get_user_read API request
        """
        test_user = 'test_user'
        url = '{0}{1}/{2}/read/'.format(local_app.config['METADATASERVICE_BASE'], USER_ENDPOINT, test_user)
        responses.add(responses.GET, url, json=self.get_user_resource_response, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/user/read', query_string=dict(user_id=test_user))
            data = json.loads(response.data)
            self.assertEquals(response.status_code, HTTPStatus.OK)
            self.assertCountEqual(data.get('read'), self.expected_parsed_user_resources)

    @responses.activate
    def test_get_user_own(self) -> None:
        """
        Test get_user_own API request
        """
        test_user = 'test_user'
        url = '{0}{1}/{2}/own/'.format(local_app.config['METADATASERVICE_BASE'], USER_ENDPOINT, test_user)
        responses.add(responses.GET, url, json=self.get_user_resource_response, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/metadata/v0/user/own', query_string=dict(user_id=test_user))
            data = json.loads(response.data)
            self.assertEquals(response.status_code, HTTPStatus.OK)
            self.assertCountEqual(data.get('own'), self.expected_parsed_user_resources)
