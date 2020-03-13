from http import HTTPStatus
from typing import Iterable, Mapping, Optional, Union

from flasgger import swag_from

from flask import request
import json

from metadata_service.api import BaseAPI
from metadata_service.entity.dashboard_detail import DashboardSchema
from metadata_service.entity.description import DescriptionSchema
from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client


class DashboardDetailAPI(BaseAPI):
    """
    Dashboard detail API
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()
        super().__init__(DashboardSchema, 'dashboard', self.client)

    @swag_from('swagger_doc/dashboard/detail_get.yml')
    def get(self, *, id: Optional[str] = None) -> Iterable[Union[Mapping, int, None]]:
        try:
            return super().get(id=id)
        except NotFoundException:
            return {'message': 'dashboard_id {} does not exist'.format(id)}, HTTPStatus.NOT_FOUND


class DashboardDescriptionAPI(BaseAPI):
    """
    DashboardDescriptionAPI supports PUT and GET operation to upsert table description
    """
    def __init__(self) -> None:
        self.client = get_proxy_client()
        super().__init__(DescriptionSchema, 'dashboard_description', self.client)

    @swag_from('swagger_doc/common/description_get.yml')
    def get(self, *, id: Optional[str] = None) -> Iterable[Union[Mapping, int, None]]:
        """
        Returns description
        """
        try:
            return super().get(id=id)

        except NotFoundException:
            return {'message': 'Dashboard {} does not exist'.format(id)}, HTTPStatus.NOT_FOUND

        except Exception:
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR

    @swag_from('swagger_doc/common/description_put.yml')
    def put(self, id: str) -> Iterable[Union[Mapping, int, None]]:
        """
        Updates Dashboard description (passed as a request body)
        :param id:
        :return:
        """
        try:
            description = json.loads(request.data).get('description')
            self.client.put_dashboard_description(id=id, description=description)
            return None, HTTPStatus.OK

        except NotFoundException:
            return {'message': 'id {} does not exist'.format(id)}, HTTPStatus.NOT_FOUND
