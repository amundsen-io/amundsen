from http import HTTPStatus
from typing import Iterable, Mapping, Union

from flask_restful import Resource, fields, marshal

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client


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
}


class UserDetailAPI(Resource):
    """
    User detail API for people resources
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    def get(self, user_id: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            # noinspection PyArgumentList
            table = self.client.get_user_detail(user_id=user_id)
            return marshal(table, user_detail_fields), HTTPStatus.OK

        except NotFoundException:
            return {'message': 'User id {} does not exist'.format(user_id)}, HTTPStatus.NOT_FOUND
