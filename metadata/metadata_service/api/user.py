# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from http import HTTPStatus
from typing import Iterable, Mapping, Optional, Union, Dict, List, Any  # noqa: F401

from amundsen_common.models.dashboard import DashboardSummarySchema
from amundsen_common.models.popular_table import PopularTableSchema
from amundsen_common.models.user import UserSchema
from flasgger import swag_from
from flask import current_app as app
from flask_restful import Resource

from metadata_service.api import BaseAPI
from metadata_service.entity.resource_type import to_resource_type, ResourceType
from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client
from metadata_service.util import UserResourceRel

LOGGER = logging.getLogger(__name__)


class UserDetailAPI(BaseAPI):
    """
    User detail API for people resources
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()
        super().__init__(UserSchema, 'user', self.client)

    @swag_from('swagger_doc/user/detail_get.yml')
    def get(self, *, id: Optional[str] = None) -> Iterable[Union[Mapping, int, None]]:
        if app.config['USER_DETAIL_METHOD']:
            try:
                user_data = app.config['USER_DETAIL_METHOD'](id)
                return UserSchema().dump(user_data).data, HTTPStatus.OK
            except Exception:
                LOGGER.exception('UserDetailAPI GET Failed - Using "USER_DETAIL_METHOD" config variable')
                return {'message': 'user_id {} fetch failed'.format(id)}, HTTPStatus.NOT_FOUND
        else:
            return super().get(id=id)


class UserFollowsAPI(Resource):
    """
    Build get API to support user follow resource features.
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/user/follow_get.yml')
    def get(self, user_id: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Return a list of resources that user has followed

        :param user_id:
        :return:
        """
        try:
            resources = self.client.get_table_by_user_relation(user_email=user_id,
                                                               relation_type=UserResourceRel.follow)

            table_key = ResourceType.Table.name.lower()
            dashboard_key = ResourceType.Dashboard.name.lower()
            result = {
                table_key: [],
                dashboard_key: []
            }  # type: Dict[str, List[Any]]

            if resources and table_key in resources and len(resources[table_key]) > 0:
                result[table_key] = PopularTableSchema(many=True).dump(resources[table_key]).data

            resources = self.client.get_dashboard_by_user_relation(user_email=user_id,
                                                                   relation_type=UserResourceRel.follow)

            if resources and dashboard_key in resources and len(resources[dashboard_key]) > 0:
                result[dashboard_key] = DashboardSummarySchema(many=True).dump(resources[dashboard_key]).data

            return result, HTTPStatus.OK

        except NotFoundException:
            return {'message': 'user_id {} does not exist'.format(user_id)}, HTTPStatus.NOT_FOUND

        except Exception:
            LOGGER.exception('UserFollowAPI GET Failed')
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR


class UserFollowAPI(Resource):
    """
    Build put / delete API to support user follow resource features.
    It will create a relationship(follow / followed_by) between user and resources(table, dashboard etc
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/user/follow_put.yml')
    def put(self, user_id: str, resource_type: str, resource_id: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Create the follow relationship between user and resources.

        :param user_id:
        :param table_uri:
        :return:
        """
        try:
            self.client.add_resource_relation_by_user(id=resource_id,
                                                      user_id=user_id,
                                                      relation_type=UserResourceRel.follow,
                                                      resource_type=to_resource_type(label=resource_type))

            return {'message': 'The user {} for id {} resource type {} '
                               'is added successfully'.format(user_id,
                                                              resource_id,
                                                              resource_type)}, HTTPStatus.OK
        except Exception as e:
            LOGGER.exception('UserFollowAPI PUT Failed')
            return {'message': 'The user {} for id {} resource type {}'
                               'is not added successfully'.format(user_id,
                                                                  resource_id,
                                                                  resource_type)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @swag_from('swagger_doc/user/follow_delete.yml')
    def delete(self, user_id: str, resource_type: str, resource_id: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Delete the follow relationship between user and resources.

        :param user_id:
        :param table_uri:
        :return:
        """
        try:
            self.client.delete_resource_relation_by_user(id=resource_id,
                                                         user_id=user_id,
                                                         relation_type=UserResourceRel.follow,
                                                         resource_type=to_resource_type(label=resource_type))
            return {'message': 'The user following {} for id {} resource type {} '
                               'is deleted successfully'.format(user_id,
                                                                resource_id,
                                                                resource_type)}, HTTPStatus.OK
        except Exception as e:
            LOGGER.exception('UserFollowAPI DELETE Failed')
            return {'message': 'The user {} for id {} resource type {} '
                               'is not deleted successfully'.format(user_id,
                                                                    resource_id,
                                                                    resource_type)}, HTTPStatus.INTERNAL_SERVER_ERROR


class UserOwnsAPI(Resource):
    """
    Build get API to support user own resource features.
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/user/own_get.yml')
    def get(self, user_id: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Return a list of resources that user has owned

        :param user_id:
        :return:
        """
        try:
            table_key = ResourceType.Table.name.lower()
            dashboard_key = ResourceType.Dashboard.name.lower()
            result = {
                table_key: [],
                dashboard_key: []
            }  # type: Dict[str, List[Any]]

            resources = self.client.get_table_by_user_relation(user_email=user_id,
                                                               relation_type=UserResourceRel.own)
            if resources and table_key in resources and len(resources[table_key]) > 0:
                result[table_key] = PopularTableSchema(many=True).dump(resources[table_key]).data

            resources = self.client.get_dashboard_by_user_relation(user_email=user_id,
                                                                   relation_type=UserResourceRel.own)

            if resources and dashboard_key in resources and len(resources[dashboard_key]) > 0:
                result[dashboard_key] = DashboardSummarySchema(many=True).dump(resources[dashboard_key]).data

            return result, HTTPStatus.OK

        except NotFoundException:
            return {'message': 'user_id {} does not exist'.format(user_id)}, HTTPStatus.NOT_FOUND

        except Exception:
            LOGGER.exception('UserOwnAPI GET Failed')
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR


class UserOwnAPI(Resource):
    """
    Build put / delete API to support user own resource features.
    It will create a relationship(owner / owner_of) between user and resources(table, dashboard etc)
    todo: Deprecate TableOwner API
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/user/own_put.yml')
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
            LOGGER.exception('UserOwnAPI PUT Failed')
            return {'message': 'The owner {} for table_uri {} '
                               'is not added successfully'.format(user_id,
                                                                  table_uri)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @swag_from('swagger_doc/user/own_delete.yml')
    def delete(self, user_id: str, resource_type: str, table_uri: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            self.client.delete_owner(table_uri=table_uri, owner=user_id)
            return {'message': 'The owner {} for table_uri {} '
                               'is deleted successfully'.format(user_id,
                                                                table_uri)}, HTTPStatus.OK
        except Exception:
            LOGGER.exception('UserOwnAPI DELETE Failed')
            return {'message': 'The owner {} for table_uri {} '
                               'is not deleted successfully'.format(user_id,
                                                                    table_uri)}, HTTPStatus.INTERNAL_SERVER_ERROR


class UserReadsAPI(Resource):
    """
    Build get API to support user read resource features.
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/user/read_get.yml')
    def get(self, user_id: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Return a list of resources that user has read

        :param user_id:
        :return:
        """
        try:
            resources = self.client.get_frequently_used_tables(user_email=user_id)
            if len(resources['table']) > 0:
                return {'table': PopularTableSchema(many=True).dump(resources['table']).data}, HTTPStatus.OK
            return {'table': []}, HTTPStatus.OK

        except NotFoundException:
            return {'message': 'user_id {} does not exist'.format(user_id)}, HTTPStatus.NOT_FOUND

        except Exception:
            LOGGER.exception('UserReadsAPI GET Failed')
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR
