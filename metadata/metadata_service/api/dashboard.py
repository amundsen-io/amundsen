from http import HTTPStatus
from typing import Iterable, Mapping, Optional, Union

from flasgger import swag_from

from metadata_service.api import BaseAPI
from metadata_service.entity.dashboard_detail import DashboardSchema
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
