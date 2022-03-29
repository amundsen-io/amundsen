# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
from http import HTTPStatus
from typing import Iterable, Mapping, Union

from amundsen_common.entity.resource_type import ResourceType
from flasgger import swag_from
from flask import request
from flask_restful import Resource, reqparse

from metadata_service.api.badge import BadgeCommon
from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client


class TypeMetadataDescriptionAPI(Resource):
    """
    TypeMetadataDescriptionAPI supports PUT and GET operations to upsert type_metadata description
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()
        super(TypeMetadataDescriptionAPI, self).__init__()

    @swag_from('swagger_doc/type_metadata/description_put.yml')
    def put(self, table_uri: str, column_name: str, type_metadata_path: str) -> Iterable[Union[dict, tuple, int, None]]:
        """
        Updates type_metadata description (passed as a request body)
        :param table_uri:
        :param column_name:
        :param type_metadata_path:
        :return:
        """
        try:
            description = json.loads(request.data).get('description')
            self.client.put_type_metadata_description(table_uri=table_uri,
                                                      column_name=column_name,
                                                      type_metadata_path=type_metadata_path,
                                                      description=description)
            return None, HTTPStatus.OK

        except NotFoundException:
            msg = 'type_metadata with key {}/{}/{} does not exist'.format(table_uri, column_name, type_metadata_path)
            return {'message': msg}, HTTPStatus.NOT_FOUND

    @swag_from('swagger_doc/type_metadata/description_get.yml')
    def get(self, table_uri: str, column_name: str, type_metadata_path: str) -> Union[tuple, int, None]:
        """
        Gets type_metadata descriptions in Neo4j
        """
        try:
            description = self.client.get_type_metadata_description(table_uri=table_uri,
                                                                    column_name=column_name,
                                                                    type_metadata_path=type_metadata_path)

            return {'description': description}, HTTPStatus.OK

        except NotFoundException:
            msg = 'type_metadata with key {}/{}/{} does not exist'.format(table_uri, column_name, type_metadata_path)
            return {'message': msg}, HTTPStatus.NOT_FOUND

        except Exception:
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR


class TypeMetadataBadgeAPI(Resource):
    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('category', type=str, required=True)
        super(TypeMetadataBadgeAPI, self).__init__()

        self._badge_common = BadgeCommon(client=self.client)

    @swag_from('swagger_doc/type_metadata/badge_put.yml')
    def put(self,
            table_uri: str,
            column_name: str,
            type_metadata_path: str,
            badge: str) -> Iterable[Union[Mapping, int, None]]:
        args = self.parser.parse_args()
        category = args.get('category', '')

        return self._badge_common.put(id=f"{table_uri}/{column_name}/{type_metadata_path}",
                                      resource_type=ResourceType.Type_Metadata,
                                      badge_name=badge,
                                      category=category)

    @swag_from('swagger_doc/type_metadata/badge_delete.yml')
    def delete(self,
               table_uri: str,
               column_name: str,
               type_metadata_path: str,
               badge: str) -> Iterable[Union[Mapping, int, None]]:
        args = self.parser.parse_args()
        category = args.get('category', '')

        return self._badge_common.delete(id=f"{table_uri}/{column_name}/{type_metadata_path}",
                                         resource_type=ResourceType.Type_Metadata,
                                         badge_name=badge,
                                         category=category)
