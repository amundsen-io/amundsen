import unittest

from http import HTTPStatus
from mock import patch

from search_service import create_app


class SearchTableFilterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.mock_index = 'fake_index'
        self.mock_term = 'test'
        self.mock_page_index = 0
        self.mock_search_request = {
            'type': 'AND',
            'filters': {
                'database': ['db1', 'db2']
            }
        }
        self.url = '/search_table'

    def tear_down(self):
        self.app_context.pop()

    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.table.get_proxy_client')
    def test_post(self, get_proxy, RequestParser) -> None:
        mock_proxy = get_proxy()
        RequestParser().parse_args.return_value = dict(index=self.mock_index,
                                                       page_index=self.mock_page_index,
                                                       query_term=self.mock_term,
                                                       search_request=self.mock_search_request)

        self.app.test_client().post(self.url)
        mock_proxy.fetch_table_search_results_with_filter.assert_called_with(index=self.mock_index,
                                                                             page_index=self.mock_page_index,
                                                                             query_term=self.mock_term,
                                                                             search_request=self.mock_search_request)

    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.table.get_proxy_client')
    def test_post_return_400_if_no_search_request(self, get_proxy, RequestParser) -> None:
        RequestParser().parse_args.return_value = dict(index=self.mock_index,
                                                       query_term=self.mock_term)

        response = self.app.test_client().post(self.url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
