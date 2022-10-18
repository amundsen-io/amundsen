
from http import HTTPStatus
import logging
import os
from typing import Dict  # noqa: F401

from sqlalchemy import create_engine, inspect

from flask import Response, jsonify, make_response, current_app as app
from marshmallow import ValidationError

# from amundsen_application.base.base_superset_preview_client import BasePreviewClient
from amundsen_application.models.preview_data import PreviewData, PreviewDataSchema, ColumnItem
from amundsen_application.client.preview.factory_base_preview_client import FactoryBasePreviewClient

# Consider a multi-database preview client
class SqlAlchemyBasePreviewClient(FactoryBasePreviewClient):

    
    def __init__(self,) -> None:
        pass

    def is_supported_preview_source(self, params: Dict, optionalHeaders: Dict = None) -> bool:
        pass

    def get_feature_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        """
        Only supports data preview currently but this function needs to be stubbed to
        implement the BasePreviewClient interface
        """
        pass

    def get_sql(self, params: Dict, optionalHeaders: Dict = None) -> str:
        pass

    def get_conn_str(self, params: Dict, optionalHeaders: Dict = None)  -> str:
        pass

    def get_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        """Preview data from SQLAlchemy accessible sources
        """
        
        if not self.is_supported_preview_source(params, optionalHeaders):
            return make_response(jsonify({'preview_data': {}}), HTTPStatus.OK)

        engine = None
        try:
            conn_str = self.get_conn_str(params=params, optionalHeaders=optionalHeaders)
            logging.info(f"conn_str={conn_str}")

            engine = create_engine(conn_str)

            sql = self.get_sql(params=params, optionalHeaders=optionalHeaders)            
            logging.info(f"sql={sql}")

            result = engine.execute(sql).fetchall()
            logging.info(f"result={result}")

            schema = params['schema']
            table = params['tableName']
            
            # now let's try to inspect the table
            inspector = inspect(engine)            
            col_meta = inspector.get_columns(table, schema=schema)
            logging.info(f"col_meta={col_meta}")
            col_names = []
            col_types = []
            for col in col_meta:
                col_names.append(col["name"])
                col_types.append(col["type"])

            logging.info(f"col_names={col_names}")
            logging.info(f"col_types={col_types}")

            rows = [dict(zip(col_names, row)) for row in result]
            logging.info(f"rows={rows}")
            column_metadata = [ColumnItem(n, t) for n, t in zip(col_names, col_types)]
            logging.info(f"column_metadata={column_metadata}")

            preview_data = PreviewData(column_metadata, rows)
            try:
                data = PreviewDataSchema().dump(preview_data)
                PreviewDataSchema().load(data)  # for validation only
                payload = jsonify({'preview_data': data})
                return make_response(payload, HTTPStatus.OK)
            except ValidationError as err:
                logging.error(f'Error(s) occurred while building preview data: {err.messages}')
                payload = jsonify({'preview_data': {}})
                return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)

        except Exception as e:
            logging.error(f'Encountered exception: {e}')
            if engine is not None:
                engine.dispose()
            
            payload = jsonify({'preview_data': {}})
            
            return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)