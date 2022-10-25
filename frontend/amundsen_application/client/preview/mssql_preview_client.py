
import logging
import os
from typing import Dict  # noqa: F401

from amundsen_application.client.preview.sqlalchemy_base_preview_client import SqlAlchemyBasePreviewClient

class MsSqlPreviewClient(SqlAlchemyBasePreviewClient):

    SQL_STATEMENT = 'SELECT TOP 50 * FROM {schema}.{table}'
    CONN_STR = 'mssql+pyodbc://{user}:{password}@{host}/{database}?driver={driver}'
    

    def __init__(self,) -> None:
        self.host = os.getenv("PREVIEW_CLIENT_MSSQL_HOST")
        self.driver = os.getenv("PREVIEW_CLIENT_MSSQL_DRIVER")
        self.username = os.getenv("PREVIEW_CLIENT_MSSQL_USERNAME")
        self.password = os.getenv("PREVIEW_CLIENT_MSSQL_PASSWORD")

        logging.info(f"host={self.host}")
        logging.info(f"driver={self.driver}")
        logging.info(f"username={self.username}")

    def _is_preview_client_configured(self) -> bool:
        return (self.driver is not None and \
                self.username is not None and \
                self.password is not None)

    def is_supported_preview_source(self, params: Dict, optionalHeaders: Dict = None) -> bool:
        warehouse_type = params.get('database')
        if warehouse_type is not None and \
           warehouse_type.lower() == 'mssql':
            if self._is_preview_client_configured():
                return True
            else:
                logging.warn('Table preview supported for source MSSQL, but the MsSqlPreviewClient was not setup correctly')
                return False
        else:
            logging.info(f'Skipping MSSQL table preview for non-MSSQL ({warehouse_type}) table')
            return False

    def get_sql(self, params: Dict, optionalHeaders: Dict = None) -> str:
        schema = params['schema']
        table = params['tableName']
        
        sql = MsSqlPreviewClient.SQL_STATEMENT.format(schema=schema, table=table)

        return sql

    def get_conn_str(self, params: Dict, optionalHeaders: Dict = None)  -> str:
        database = params['cluster']
        
        conn_str = MsSqlPreviewClient.CONN_STR.format(
            user=self.username,
            password=self.password,
            driver=self.driver,
            database=database,
            host=self.host
        )

        return conn_str
