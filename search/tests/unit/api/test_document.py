import unittest

from http import HTTPStatus
from mock import patch, Mock

from search_service.api.document import DocumentTableAPI, DocumentUserAPI
from search_service import create_app


class DocumentTableAPITest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.Config')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tear_down(self):
        self.app_context.pop()

    @patch('search_service.api.document.TableSchema')
    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.document.get_proxy_client')
    def test_post(self, get_proxy, RequestParser, TableSchema) -> None:
        mock_proxy = get_proxy.return_value = Mock()
        RequestParser().parse_args.return_value = dict(data='{}', index='fake_index')
        expected_value = TableSchema().loads.return_value = Mock()

        response = DocumentTableAPI().post()
        self.assertEqual(list(response)[1], HTTPStatus.OK)
        mock_proxy.create_document.assert_called_with(data=expected_value, index='fake_index')

    @patch('search_service.api.document.TableSchema')
    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.document.get_proxy_client')
    def test_put(self, get_proxy, RequestParser, TableSchema) -> None:
        mock_proxy = get_proxy.return_value = Mock()
        RequestParser().parse_args.return_value = dict(data='{}', index='fake_index')
        expected_value = TableSchema().loads.return_value = Mock()

        response = DocumentTableAPI().put()
        self.assertEqual(list(response)[1], HTTPStatus.OK)
        mock_proxy.update_document.assert_called_with(data=expected_value, index='fake_index')

    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.document.get_proxy_client')
    def test_delete(self, get_proxy, RequestParser) -> None:
        mock_proxy = get_proxy.return_value = Mock()
        RequestParser().parse_args.return_value = dict(data='[]', index='fake_index')

        response = DocumentTableAPI().delete(document_id='fake id')
        self.assertEqual(list(response)[1], HTTPStatus.OK)
        mock_proxy.delete_document.assert_called_with(data=['fake id'], index='fake_index')


class DocumentUserAPITest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.Config')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tear_down(self):
        self.app_context.pop()

    @patch('search_service.api.document.UserSchema')
    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.document.get_proxy_client')
    def test_post(self, get_proxy, RequestParser, UserSchema) -> None:
        mock_proxy = get_proxy.return_value = Mock()
        RequestParser().parse_args.return_value = dict(data='{}', index='fake_index')
        expected_value = UserSchema().loads.return_value = Mock()

        response = DocumentUserAPI().post()
        self.assertEqual(list(response)[1], HTTPStatus.OK)
        mock_proxy.create_document.assert_called_with(data=expected_value, index='fake_index')

    @patch('search_service.api.document.UserSchema')
    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.document.get_proxy_client')
    def test_put(self, get_proxy, RequestParser, UserSchema) -> None:
        mock_proxy = get_proxy.return_value = Mock()
        RequestParser().parse_args.return_value = dict(data='{}', index='fake_index')
        expected_value = UserSchema().loads.return_value = Mock()

        response = DocumentUserAPI().put()
        self.assertEqual(list(response)[1], HTTPStatus.OK)
        mock_proxy.update_document.assert_called_with(data=expected_value, index='fake_index')

    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.document.get_proxy_client')
    def test_delete(self, get_proxy, RequestParser) -> None:
        mock_proxy = get_proxy.return_value = Mock()
        RequestParser().parse_args.return_value = dict(data='[]', index='fake_index')

        response = DocumentUserAPI().delete(document_id='fake id')
        self.assertEqual(list(response)[1], HTTPStatus.OK)
        mock_proxy.delete_document.assert_called_with(data=['fake id'], index='fake_index')
