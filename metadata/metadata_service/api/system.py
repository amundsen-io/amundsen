from http import HTTPStatus
from typing import Iterable, Union, Mapping

from flask_restful import Resource

from metadata_service.proxy import neo4j_proxy


class Neo4jDetailAPI(Resource):
    """
    API to fetch system information for neo4j
    """

    def __init__(self) -> None:
        self.neo4j = neo4j_proxy.get_neo4j()

    def get(self) -> Iterable[Union[Mapping, int, None]]:
        last_updated_ts = self.neo4j.get_neo4j_latest_updated_ts()
        if last_updated_ts is not None:
            return {'neo4j_latest_timestamp': int(last_updated_ts)}, HTTPStatus.OK
        else:
            return {'message': 'neo4j / es hasnt been updated / indexed.'}, HTTPStatus.NO_CONTENT
