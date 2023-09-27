import json
from http import HTTPStatus
from typing import Any, Iterable, Mapping, Optional, Union
import logging

from amundsen_common.entity.resource_type import ResourceType
from amundsen_common.models.lineage import LineageSchema
from amundsen_common.models.snowflake.snowflake import SnowflakeTableSharesSchema
from flasgger import swag_from
from flask_restful import Resource, fields, marshal

from metadata_service.api import BaseAPI
from metadata_service.api.badge import BadgeCommon
from metadata_service.api.tag import TagCommon
from metadata_service.entity.dashboard_summary import DashboardSummarySchema
from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client


LOGGER = logging.getLogger(__name__)

snowflake_listing_fields = {
    'global_name': fields.String,
    'name': fields.String,
    'title': fields.String,
    'subtitle': fields.String,
    'description': fields.String
}

snowflake_table_share_fields = {
    'owner_account': fields.String,
    'name': fields.String,
    'listing': fields.Nested(snowflake_listing_fields)
}

snowflake_table_shares_fields = {
    'snowflake_table_shares': fields.List(fields.Nested(snowflake_table_share_fields))
}

class SnowflakeTableShareAPI(Resource):
    """
    SnowflakeTableShare API
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('../swagger_doc/snowflake/snowflake_table_share_get.yml')
    def get(self, table_uri: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            snowflake_table_shares = self.client.get_snowflake_table_shares(table_uri=table_uri)
            # LOGGER.info(f"snowflake_table_shares={snowflake_table_shares}")
            return marshal({'snowflake_table_shares': snowflake_table_shares}, snowflake_table_shares_fields), HTTPStatus.OK
            # schema = SnowflakeTableSharesSchema()
            # return schema.dump(snowflake_table_shares), HTTPStatus.OK

        except NotFoundException:
            return {'message': 'table_uri {} does not exist'.format(table_uri)}, HTTPStatus.NOT_FOUND