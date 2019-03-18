from http import HTTPStatus
from typing import Iterable, Union, Mapping

from flask_restful import Resource, fields, marshal

from metadata_service.proxy import get_proxy_client

tag_fields = {
    'tag_name': fields.String,
    'tag_count': fields.Integer
}


tag_usage_fields = {
    'tag_usages': fields.List(fields.Nested(tag_fields))
}


class TagAPI(Resource):
    def __init__(self) -> None:
        self.client = get_proxy_client()
        super(TagAPI, self).__init__()

    def get(self) -> Iterable[Union[Mapping, int, None]]:
        """
        API to fetch all the existing tags with usage.
        """
        tag_usages = self.client.get_tags()
        return marshal({'tag_usages': tag_usages}, tag_usage_fields), HTTPStatus.OK
