from http import HTTPStatus
from typing import Iterable, Mapping, Union

from flask_restful import Resource, fields, marshal

from metadata_service.api.table import table_detail_fields
from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client
from metadata_service.util import UserResourceRel


user_detail_fields = {
    'email': fields.String,
    'first_name': fields.String,  # Optional
    'last_name': fields.String,  # Optional
    'full_name': fields.String,  # Optional
    'is_active': fields.Boolean,  # Optional
    'github_username': fields.String,  # Optional
    'slack_id': fields.String,  # Optional
    'team_name': fields.String,  # Optional
    'employee_type': fields.String,  # Optional
    'manager_fullname': fields.String,  # Optional
}

table_list_fields = {
    'table': fields.List(fields.Nested(table_detail_fields))
}


class UserDetailAPI(Resource):
    """
    User detail API for people resources
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    def get(self, user_id: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            table = self.client.get_user_detail(user_id=user_id)
            return marshal(table, user_detail_fields), HTTPStatus.OK

        except NotFoundException:
            return {'message': 'User id {} does not exist'.format(user_id)}, HTTPStatus.NOT_FOUND


class UserFollowAPI(Resource):
    """
    Build get / put API to support user follow resource features.
    It will create a relationship(follow / followed_by) between user and resources(table, dashboard etc)
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    def get(self, user_id: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Return a list of resources that user has followed

        :param user_id:
        :return:
        """
        try:
            resources = self.client.get_table_by_user_relation(user_email=user_id,
                                                               relation_type=UserResourceRel.follow)
            return marshal(resources, table_list_fields), HTTPStatus.OK

        except NotFoundException:
            return {'message': 'user_id {} does not exist'.format(user_id)}, HTTPStatus.NOT_FOUND

        except Exception:
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR

    def put(self, user_id: str, resource_type: str, table_uri: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Create the follow relationship between user and resources.
        todo: It will need to refactor all neo4j proxy api to take a type argument.

        :param user_id:
        :param table_uri:
        :return:
        """
        try:
            self.client.add_table_relation_by_user(table_uri=table_uri,
                                                   user_email=user_id,
                                                   relation_type=UserResourceRel.follow)
            return {'message': 'The user {} for table_uri {} '
                               'is added successfully'.format(user_id,
                                                              table_uri)}, HTTPStatus.OK
        except Exception as e:
            return {'message': 'The user {} for table_uri {} '
                               'is not added successfully'.format(user_id,
                                                                  table_uri)}, \
                HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self, user_id: str, resource_type: str, table_uri: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Delete the follow relationship between user and resources.
        todo: It will need to refactor all neo4j proxy api to take a type argument.

        :param user_id:
        :param table_uri:
        :return:
        """
        try:
            self.client.delete_table_relation_by_user(table_uri=table_uri,
                                                      user_email=user_id,
                                                      relation_type=UserResourceRel.follow)
            return {'message': 'The user {} for table_uri {} '
                               'is added successfully'.format(user_id,
                                                              table_uri)}, HTTPStatus.OK
        except Exception as e:
            return {'message': 'The user {} for table_uri {} '
                               'is not added successfully'.format(user_id,
                                                                  table_uri)}, \
                HTTPStatus.INTERNAL_SERVER_ERROR


class UserOwnAPI(Resource):
    """
    Build get / put API to support user own resource features.
    It will create a relationship(owner / owner_of) between user and resources(table, dashboard etc)
    todo: Deprecate TableOwner API
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    def get(self, user_id: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Return a list of resources that user has owned

        :param user_id:
        :return:
        """
        try:
            resources = self.client.get_table_by_user_relation(user_email=user_id,
                                                               relation_type=UserResourceRel.own)
            return marshal(resources, table_list_fields), HTTPStatus.OK

        except NotFoundException:
            return {'message': 'user_id {} does not exist'.format(user_id)}, HTTPStatus.NOT_FOUND

        except Exception:
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR

    def put(self, user_id: str, resource_type: str, table_uri: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Create the follow relationship between user and resources.

        :param user_id:
        :param resource_type:
        :param table_uri:
        :return:
        """
        try:
            self.client.add_owner(table_uri=table_uri, owner=user_id)
            return {'message': 'The owner {} for table_uri {} '
                               'is added successfully'.format(user_id,
                                                              table_uri)}, HTTPStatus.OK
        except Exception as e:
            return {'message': 'The owner {} for table_uri {} '
                               'is not added successfully'.format(user_id,
                                                                  table_uri)}, HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self, user_id: str, resource_type: str, table_uri: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            self.client.delete_owner(table_uri=table_uri, owner=user_id)
            return {'message': 'The owner {} for table_uri {} '
                               'is deleted successfully'.format(user_id,
                                                                table_uri)}, HTTPStatus.OK
        except Exception:
            return {'message': 'The owner {} for table_uri {} '
                               'is not deleted successfully'.format(user_id,
                                                                    table_uri)}, HTTPStatus.INTERNAL_SERVER_ERROR


class UserReadAPI(Resource):
    """
    Build get / put API to support user read resource features.
    It will create a relationship(read / read_by) between user and resources(table, dashboard etc)
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    def get(self, user_id: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Return a list of resources that user has read

        :param user_id:
        :return:
        """
        try:
            resources = self.client.get_table_by_user_relation(user_email=user_id,
                                                               relation_type=UserResourceRel.read)
            return marshal(resources, table_list_fields), HTTPStatus.OK

        except NotFoundException:
            return {'message': 'user_id {} does not exist'.format(user_id)}, HTTPStatus.NOT_FOUND

        except Exception:
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR
