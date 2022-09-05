import logging
from http import HTTPStatus
from ast import literal_eval
from flasgger import swag_from
from typing import Iterable, Mapping, Union
from marshmallow.exceptions import ValidationError
from metadata_service.entity.resource_type import ResourceType

from metadata_service.proxy import get_proxy_client
from metadata_service.entity.service import ServiceSchema
from flask_restful import Resource, fields, marshal, reqparse
from metadata_service.exception import NotFoundException
from metadata_service.api.attribute import AttributeCommon

LOGGER = logging.getLogger(__name__)

class ServiceAttributeAPI(Resource):
    """
    ServiceAttributeAPI that supports GET, PUT and DELETE operation to add or delete attribute
    on service
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('description', type=str, required=False, default='')
        super(ServiceAttributeAPI, self).__init__()

        self._attribute_common = AttributeCommon(client=self.client)

    @swag_from('swagger_doc/attribute/attribute_put.yml')
    def put(self, id: str, name: str) -> Iterable[Union[Mapping, int, None]]:
        """
        API to add a attribute to existing table uri.

        :param service_key:
        :param name:
        :param description:
        :return:
        """
        args = self.parser.parse_args()
        # use tag_type to distinguish between tag and badge
        description = args.get('description', 'test')
        return self._attribute_common.put(id=id,
                                    resource_type=ResourceType.Service,
                                    name=name,
                                    description=description)



class ServiceAddAPI(Resource):

    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        super(ServiceAddAPI, self).__init__()


    @swag_from('swagger_doc/service/service_put.yml')
    def put(self) -> Iterable[Union[Mapping, int, None]]:

        self.parser.add_argument('data', required=True)
        args = self.parser.parse_args()

        try:
            data = literal_eval(args.get('data'))
            try: #todo-falcon
                service_data = ServiceSchema().load(data)
            except ValidationError as e:
                logging.warning("Invalid input: %s", e.messages)
                raise ValidationError("Invalid input")
            self.client.add_service(service=service_data)
            return {'message': f'The service {service_data.name}'
                               ' was added successfully'}, HTTPStatus.OK
        except RuntimeError as e:
            LOGGER.error(f'Internal server error occurred when adding service: {e}')
            return {'message': f'The service was not added successfully. Message: {e}'}, HTTPStatus.INTERNAL_SERVER_ERROR
   

class ServiceDetailAPI(Resource):
    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/service/detail_get.yml')
    def get(self, service_key: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            service = self.client.get_service(service_key=service_key)
            schema = ServiceSchema()
            return schema.dump(service), HTTPStatus.OK
        except NotFoundException:
            LOGGER.error(f'NotFoundException: service_key {service_key} does not exist')
            return {'message': f'service_key {service_key} does not exist'}, HTTPStatus.NOT_FOUND
        except Exception as e:
            LOGGER.error(f'Internal server error occurred when getting service details: {e}')
            return {'message': f'Internal server error: {e}'}, HTTPStatus.INTERNAL_SERVER_ERROR
