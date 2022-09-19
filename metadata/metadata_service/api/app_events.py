import logging
from http import HTTPStatus
from ast import literal_eval
from flasgger import swag_from
from typing import Iterable, Mapping, Union
from marshmallow.exceptions import ValidationError
from metadata_service.entity.resource_type import ResourceType

from metadata_service.proxy import get_proxy_client
from metadata_service.entity.app_events import AppEventsSchema
from flask_restful import Resource, fields, marshal, reqparse
from metadata_service.exception import NotFoundException
from metadata_service.api.attribute import AttributeCommon

LOGGER = logging.getLogger(__name__)



class EventAttributeAPI(Resource):
    """
    EventAttributeAPI that supports GET, PUT and DELETE operation to add or delete attribute
    on events
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('description', type=str, required=False, default='')
        super(EventAttributeAPI, self).__init__()

        self._attribute_common = AttributeCommon(client=self.client)

    @swag_from('swagger_doc/attribute/attribute_put.yml')
    def put(self, id: str, name: str) -> Iterable[Union[Mapping, int, None]]:
        """
        API to add a attribute to existing table uri.

        :param event_key:
        :param name:
        :param description:
        :return:
        """
        args = self.parser.parse_args()
        # use tag_type to distinguish between tag and badge
        description = args.get('description', 'test')
        return self._attribute_common.put(id=id,
                                    resource_type=ResourceType.Events,
                                    name=name,
                                    description=description)



class AppEventsAddAPI(Resource):

    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        super(AppEventsAddAPI, self).__init__()


    @swag_from('swagger_doc/app_events/app_events_put.yml')
    def put(self) -> Iterable[Union[Mapping, int, None]]:
        self.parser.add_argument('data', required=True)
        args = self.parser.parse_args()
        try:
            data = literal_eval(args.get('data'))
            try: 
                app_event_data = AppEventsSchema().load(data)
            except ValidationError as e:
                logging.warning("Invalid input: %s", e.messages)
                raise ValidationError("Invalid input")
            self.client.add_app_event(events=app_event_data)
            return {'message': f'The app event {app_event_data.name}'
                               ' was added successfully'}, HTTPStatus.OK
        except RuntimeError as e:
            LOGGER.error(f'Internal server error occurred when adding app event: {e}')
            return {'message': f'The app event was not added successfully. Message: {e}'}, HTTPStatus.INTERNAL_SERVER_ERROR
   

class AppEventDetailAPI(Resource):
    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/app_events/detail_get.yml')
    def get(self, key: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            events = self.client.get_app_event(key=key)
            schema = AppEventsSchema()
            return schema.dump(events), HTTPStatus.OK
        except NotFoundException:
            LOGGER.error(f'NotFoundException: app event key {events} does not exist')
            return {'message': f'app event key {events} does not exist'}, HTTPStatus.NOT_FOUND
        except Exception as e:
            LOGGER.error(f'Internal server error occurred when getting app event details: {e}')
            return {'message': f'Internal server error: {e}'}, HTTPStatus.INTERNAL_SERVER_ERROR
