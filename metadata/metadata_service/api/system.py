# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Iterable, Union, Mapping

from flask_restful import Resource
from flasgger import swag_from

from metadata_service.proxy import get_proxy_client


class Neo4jDetailAPI(Resource):
    """
    API to fetch system information for neo4j
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/neo4j/detail_get.yml')
    def get(self) -> Iterable[Union[Mapping, int, None]]:
        last_updated_ts = self.client.get_latest_updated_ts()
        if last_updated_ts is not None:
            return {'neo4j_latest_timestamp': int(last_updated_ts)}, HTTPStatus.OK
        else:
            return {'message': 'neo4j / es hasnt been updated / indexed.'}, HTTPStatus.NO_CONTENT
