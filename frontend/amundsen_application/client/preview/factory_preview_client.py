
from typing import Dict
import logging
from http import HTTPStatus
from typing import Dict  # noqa: F401

from flask import Response, jsonify, make_response

from amundsen_application.client.preview.factory_base_preview_client import FactoryBasePreviewClient
from amundsen_application.client.preview.dremio_preview_client import DremioPreviewClient
from amundsen_application.client.preview.mssql_preview_client import MsSqlPreviewClient
from amundsen_application.client.preview.snowflake_preview_client import SnowflakePreviewClient  # noqa: F401
from amundsen_application.base.base_superset_preview_client import BasePreviewClient


class FactoryPreviewClient(BasePreviewClient):

    def __init__(self,) -> None:
        self.preview_clients = []
        self.preview_clients.append(DremioPreviewClient())
        self.preview_clients.append(SnowflakePreviewClient())
        self.preview_clients.append(MsSqlPreviewClient())

    def get_feature_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        pass

    def get_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        response: Response = None
        
        for preview_client in self.preview_clients:            
            if preview_client.is_supported_preview_source(params, optionalHeaders):
                response = preview_client.get_preview_data(params, optionalHeaders)
                break
    
        if response == None:
            logging.warning(f'Unsupported dataset source for preview client: {params}')
            response = make_response(jsonify({'preview_data': {}}), HTTPStatus.OK)
        
        return response
        
        

    def is_supported_preview_source(self, params: Dict, optionalHeaders: Dict = None) -> bool:
        pass