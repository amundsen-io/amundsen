
from typing import Dict
import logging
from http import HTTPStatus
from typing import Dict  # noqa: F401

from flask import Response, jsonify, make_response

from amundsen_application.client.preview.factory_base_preview_client import FactoryBasePreviewClient
from amundsen_application.client.preview.dremio_preview_client import DremioPreviewClient
from amundsen_application.client.preview.snowflake_preview_client import SnowflakePreviewClient  # noqa: F401
from amundsen_application.base.base_superset_preview_client import BasePreviewClient


class FactoryPreviewClient(BasePreviewClient):

    def __init__(self,) -> None:
        self.dremio_preview_client: FactoryBasePreviewClient = DremioPreviewClient()
        self.snowflake_preview_client: FactoryBasePreviewClient = SnowflakePreviewClient()


    def get_feature_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        pass

    def get_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        if self.dremio_preview_client.is_supported_preview_source(params, optionalHeaders):
            return self.dremio_preview_client.get_preview_data(params, optionalHeaders)
        elif self.snowflake_preview_client.is_supported_preview_source(params, optionalHeaders):
            return self.snowflake_preview_client.get_preview_data(params, optionalHeaders)
        else:
            logging.warn(f'Unsupported dataset source for preview client: {params}')
            return make_response(jsonify({'preview_data': {}}), HTTPStatus.OK)
        

    def is_supported_preview_source(self, params: Dict, optionalHeaders: Dict = None) -> bool:
        pass