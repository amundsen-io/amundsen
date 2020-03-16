import unittest

from amundsen_application.api.utils.metadata_utils import marshall_table_full
from amundsen_application import create_app

local_app = create_app('amundsen_application.config.TestConfig', 'tests/templates')


class MetadataUtilsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.input_data = {
            'cluster': 'test_cluster',
            'columns': [
                {
                    'name': 'column_1',
                    'description': 'This is a test',
                    'col_type': 'bigint',
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
            'name': 'test_table',
            'table_description': 'This is a test',
            'tags': [],
            'table_readers': [
                {'user': {'email': 'test@test.com', 'first_name': None, 'last_name': None}, 'read_count': 100}
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
            'programmatic_descriptions': [
                {'source': 'c_1', 'text': 'description c'},
                {'source': 'a_1', 'text': 'description a'},
                {'source': 'b_1', 'text': 'description b'}
            ]
        }

        self.expected_data = {'badges': [],
                              'cluster': 'test_cluster',
                              'columns': [{'col_type': 'bigint',
                                           'description': 'This is a test',
                                           'name': 'column_1',
                                           'sort_order': 0,
                                           'stats': [{'end_epoch': 1538352000,
                                                      'start_epoch': 1538352000,
                                                      'stat_type': 'count',
                                                      'stat_val': '100'},
                                                     {'end_epoch': 1538352000,
                                                      'start_epoch': 1538352000,
                                                      'stat_type': 'count_null',
                                                      'stat_val': '0'}]}],
                              'database': 'test_db',
                              'description': None,
                              'is_editable': True,
                              'is_view': False,
                              'key': 'test_db://test_cluster.test_schema/test_table',
                              'last_updated_timestamp': None,
                              'name': 'test_table',
                              'owners': [],
                              'partition': {'is_partitioned': True, 'key': 'ds', 'value': ''},
                              'programmatic_descriptions': [{'source': 'a_1', 'text': 'description a'},
                                                            {'source': 'c_1', 'text': 'description c'},
                                                            {'source': 'b_1', 'text': 'description b'}],
                              'schema': 'test_schema',
                              'source': None,
                              'table_readers': [{'read_count': 100,
                                                 'user': {'display_name': 'test@test.com',
                                                          'email': 'test@test.com',
                                                          'employee_type': None,
                                                          'first_name': None,
                                                          'full_name': None,
                                                          'github_username': None,
                                                          'is_active': True,
                                                          'last_name': None,
                                                          'manager_email': None,
                                                          'manager_fullname': None,
                                                          'profile_url': '',
                                                          'role_name': None,
                                                          'slack_id': None,
                                                          'team_name': None,
                                                          'user_id': 'test@test.com'}}],
                              'table_writer': {'application_url': 'https://test-test.test.test',
                                               'description': 'This is a test',
                                               'id': 'test_id',
                                               'kind': None,
                                               'name': 'test_name'},
                              'tags': [],
                              'watermarks': [{'create_time': '',
                                              'partition_key': 'ds',
                                              'partition_value': '',
                                              'watermark_type': 'low_watermark'},
                                             {'create_time': '',
                                              'partition_key': 'ds',
                                              'partition_value': '',
                                              'watermark_type': 'high_watermark'}]}

    def test_marshal_table_full(self) -> None:
        with local_app.app_context():
            actual_result = marshall_table_full(self.input_data)
            self.assertEqual(actual_result, self.expected_data)
