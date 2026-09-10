# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from http import HTTPStatus
from typing import Iterable, Mapping, Union

from amundsen_common.entity.resource_type import ResourceType
from flasgger import swag_from
from flask import request
from flask_restful import Resource, reqparse

from metadata_service.api.badge import BadgeCommon
from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client

LOGGER = logging.getLogger(__name__)


class TypeMetadataDescriptionAPI(Resource):
    """
    TypeMetadataDescriptionAPI supports PUT and GET operations to upsert type_metadata description
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()
        super(TypeMetadataDescriptionAPI, self).__init__()

    @swag_from('swagger_doc/type_metadata/description_put.yml')
    def put(self, type_metadata_key: str) -> Iterable[Union[dict, tuple, int, None]]:
        """
        Updates type_metadata description (passed as a request body)
        :param type_metadata_key:
        :return:
        """
        try:
            description = json.loads(request.data).get('description')
            self.client.put_type_metadata_description(type_metadata_key=type_metadata_key,
                                                      description=description)
            return None, HTTPStatus.OK

        except NotFoundException:
            msg = f'type_metadata with key {type_metadata_key} does not exist'
            LOGGER.error(f'NotFoundException: {msg}')
            return {'message': msg}, HTTPStatus.NOT_FOUND

    @swag_from('swagger_doc/type_metadata/description_get.yml')
    def get(self, type_metadata_key: str) -> Union[tuple, int, None]:
        """
        Gets type_metadata descriptions in Neo4j
        """
        try:
            description = self.client.get_type_metadata_description(type_metadata_key=type_metadata_key)

            return {'description': description}, HTTPStatus.OK

        except NotFoundException:
            msg = f'type_metadata with key {type_metadata_key} does not exist'
            LOGGER.error(f'NotFoundException: {msg}')
            return {'message': msg}, HTTPStatus.NOT_FOUND

        except Exception as e:
            LOGGER.error(f'Internal server error occurred when getting type metadata description: {e}')
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR


class TypeMetadataBadgeAPI(Resource):
    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('category', type=str, required=True)
        super(TypeMetadataBadgeAPI, self).__init__()

        self._badge_common = BadgeCommon(client=self.client)

    @swag_from('swagger_doc/type_metadata/badge_put.yml')
    def put(self, type_metadata_key: str, badge: str) -> Iterable[Union[Mapping, int, None]]:
        args = self.parser.parse_args()
        category = args.get('category', '')

        return self._badge_common.put(id=type_metadata_key,
                                      resource_type=ResourceType.Type_Metadata,
                                      badge_name=badge,
                                      category=category)

    @swag_from('swagger_doc/type_metadata/badge_delete.yml')
    def delete(self, type_metadata_key: str, badge: str) -> Iterable[Union[Mapping, int, None]]:
        args = self.parser.parse_args()
        category = args.get('category', '')

        return self._badge_common.delete(id=type_metadata_key,
                                         resource_type=ResourceType.Type_Metadata,
                                         badge_name=badge,
                                         category=category)
