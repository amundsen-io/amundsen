
from http import HTTPStatus
import logging
import os
from typing import Dict  # noqa: F401

from flask import Response, jsonify, make_response, current_app as app
from marshmallow import ValidationError
from pyarrow import flight

from sqlalchemy import create_engine

from amundsen_application.client.preview.sqlalchemy_base_preview_client import SqlAlchemyBasePreviewClient



class DremioPreviewClient(SqlAlchemyBasePreviewClient):

    SQL_STATEMENT = 'SELECT * FROM {schema}."{table}" LIMIT 50'
    CONN_STR = 'dremio://{username}:{password}@{host}:{port}/dremio;SSL=0'


    def __init__(self,) -> None:
        self.host = os.getenv("PREVIEW_CLIENT_DREMIO_HOST")
        self.port = os.getenv("PREVIEW_CLIENT_DREMIO_PORT")
        self.username = os.getenv("PREVIEW_CLIENT_DREMIO_USERNAME")
        self.password = os.getenv("PREVIEW_CLIENT_DREMIO_PASSWORD")

        logging.info(f"host={self.host}")
        logging.info(f"port={self.port}")
        logging.info(f"username={self.username}")

    def _is_preview_client_configured(self) -> bool:
        return (self.host is not None and \
                self.port is not None and \
                self.username is not None and \
                self.password is not None)

    def is_supported_preview_source(self, params: Dict, optionalHeaders: Dict = None) -> bool:
        warehouse_type = params.get('database')
        if warehouse_type is not None and \
           warehouse_type.lower() == 'dremio':
            if self._is_preview_client_configured():
                return True
            else:
                logging.warn('Table preview supported for source Dremio, but the DremioPreviewClient was not setup correctly')
                return False
        else:
            logging.info(f'Skipping Dremio table preview for non-Dremio ({warehouse_type}) table')
            return False

    def get_sql(self, params: Dict, optionalHeaders: Dict = None) -> str:
        schema = '"{}"'.format(params['schema'].replace('.', '"."'))
        table = params['tableName']

        sql = DremioPreviewClient.SQL_STATEMENT.format(schema=schema,
                                                       table=table)

        return sql

    def get_conn_str(self, params: Dict, optionalHeaders: Dict = None)  -> str:
        conn_str = DremioPreviewClient.CONN_STR.format(username=self.username,
                                                       password=self.password,
                                                       host=self.host,
                                                       port=self.port) 
        return conn_str