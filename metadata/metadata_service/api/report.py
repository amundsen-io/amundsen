import json
import logging
from http import HTTPStatus
from typing import Iterable, Mapping, Union

from flask_restful import Resource, reqparse

from metadata_service.exception import NotFoundException
from metadata_service.models.reports import ReportSchema
from metadata_service.proxy import get_proxy_client


class ReportDetailAPI(Resource):
    """
    ReportDetailAPI API
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    def get(self, report_key: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            report = self.client.get_report(report_key=report_key)
            schema = ReportSchema()
            returnObject = schema.dump(report)
            logging.warning(returnObject)
            return returnObject, HTTPStatus.OK

        except NotFoundException:
            return {'message': 'report_key {} does not exist'.format(report_key)}, HTTPStatus.NOT_FOUND