
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
class SnowflakePreviewClient(FactoryBasePreviewClient):

    SQL_STATEMENT = 'SELECT * FROM {database}.{schema}.{table} LIMIT 50'
    SNOWFLAKE_CONN_STR = 'snowflake://{user}:{password}@{account_identifier}/{database}/{schema}>?warehouse={warehouse}&role={role}'
    # 'snowflake://<user_login_name>:<password>@<account_identifier>/<database_name>/<schema_name>?warehouse=<warehouse_name>&role=<role_name>'

    

    def __init__(self,) -> None:
        self.account_identifier = os.getenv("PREVIEW_CLIENT_SNOWFLAKE_ACCOUNT_IDENTIFIER")
        self.warehouse = os.getenv("PREVIEW_CLIENT_SNOWFLAKE_WAREHOUSE")
        self.role = os.getenv("PREVIEW_CLIENT_SNOWFLAKE_ROLE")
        self.username = os.getenv("PREVIEW_CLIENT_SNOWFLAKE_USERNAME")
        self.password = os.getenv("PREVIEW_CLIENT_SNOWFLAKE_PASSWORD")

        logging.info(f"account_identifier={self.account_identifier}")
        logging.info(f"warehouse={self.warehouse}")
        logging.info(f"role={self.role}")
        logging.info(f"username={self.username}")

    def _is_preview_client_configured(self) -> bool:
        return (self.account_identifier is not None and \
                self.warehouse is not None and \
                self.role is not None and \
                self.username is not None and \
                self.password is not None)

    def is_supported_preview_source(self, params: Dict, optionalHeaders: Dict = None) -> bool:
        warehouse_type = params.get('database')
        if warehouse_type is not None and \
           warehouse_type.lower() == 'snowflake':
            if self._is_preview_client_configured():
                return True
            else:
                logging.warn('Table preview supported for source Snowflake, but the SnowflakePreviewClient was not setup correctly')
                return False
        else:
            logging.info(f'Skipping Snowflake table preview for non-Snowflake ({warehouse_type}) table')
            return False

    def get_feature_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        """
        SnowflakePreviewClient only supports data preview currently but this function needs to be stubbed to
        implement the BasePreviewClient interface
        """
        pass

    def get_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        """Preview data from Snowflake source
        """
        
        if not self.is_supported_preview_source(params, optionalHeaders):
            return make_response(jsonify({'preview_data': {}}), HTTPStatus.OK)

        try:
            

            # Format base SQL_STATEMENT with request table and schema
            # schema = '"{}"'.format(params['schema'].replace('.', '"."'))
            schema = params['schema']
            table = params['tableName']
            database = params['cluster']
            

            conn_str = SnowflakePreviewClient.SNOWFLAKE_CONN_STR.format(
                user=self.username,
                password=self.password,
                account_identifier=self.account_identifier,
                database=database,
                schema=schema,
                warehouse=self.warehouse,
                role=self.role)

            engine = create_engine(conn_str)

            sql = SnowflakePreviewClient.SQL_STATEMENT.format(database=database,
                                                              schema=schema,
                                                              table=table)

            logging.info(f"sql={sql}")

            # client = flight.FlightClient(self.url, **self.connection_args)
            # client.authenticate(_DremioAuthHandler(self.username, self.password))
            # flight_descriptor = flight.FlightDescriptor.for_command(sql)
            # flight_info = client.get_flight_info(flight_descriptor)
            # reader = client.do_get(flight_info.endpoints[0].ticket)
            result = engine.execute(sql).fetchall()

            logging.info(f"result={result}")
            
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

            # columns = map(lambda x: x.to_pylist(), result)
            # logging.info(f"columns={columns}")
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