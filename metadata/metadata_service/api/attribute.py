# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Iterable, Mapping, Tuple, Union

from amundsen_common.entity.resource_type import ResourceType
from flasgger import swag_from
from flask import current_app as app
from flask_restful import Resource, fields, marshal

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client
from metadata_service.proxy.base_proxy import BaseProxy

attribute_fields = {
    'name': fields.String,
    'attribute_count' : fields.Integer
}
attribute_details_fields = {
    'attribute_usage': fields.List(fields.Nested(attribute_fields))
}


class AttributeAPI(Resource):
    def __init__(self) -> None:
        self.client = get_proxy_client()
        super(AttributeAPI, self).__init__()

    @swag_from('swagger_doc/attribute/attribute_get.yml')
    def get(self) -> Iterable[Union[Mapping, int, None]]:
        """
        API to fetch all the existing attributes with count.
        """
        attr_details = self.client.get_attribute()
        return marshal({'attribute_usage': attr_details}, attribute_details_fields), HTTPStatus.OK


class AttributeCommon:
    def __init__(self, client: BaseProxy) -> None:
        self.client = client

    def put(self, id: str, resource_type: ResourceType,
            name: str, description: str) -> Tuple[Any, HTTPStatus]:
        """
        Method to add a attribute to existing resource.

        :param id:
        :param resource_type:
        :param name:
        :param description:
        :return:
        """
        try:
            self.client.add_attribute(id=id,
                                    name=name,
                                    description=description,
                                    resource_type=resource_type)
            return {'message': 'The attribute {} for id {} with type {} and resource_type {} '
                                   'is added successfully'.format(name,
                                                                  id,
                                                                  description,
                                                                  resource_type.name)}, HTTPStatus.OK
        except NotFoundException:
                return \
                    {'message': 'The attribute {}  with type {} and resource_type {} '
                                'is not added successfully'.format(name,
                                                                   description,
                                                                   resource_type.name)}, \
                    HTTPStatus.NOT_FOUND