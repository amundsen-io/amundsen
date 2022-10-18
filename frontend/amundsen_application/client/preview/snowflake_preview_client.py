
import logging
import os
from typing import Dict  # noqa: F401

from amundsen_application.client.preview.sqlalchemy_base_preview_client import SqlAlchemyBasePreviewClient

class SnowflakePreviewClient(SqlAlchemyBasePreviewClient):

    SQL_STATEMENT = 'SELECT * FROM {database}.{schema}.{table} LIMIT 50'
    CONN_STR = 'snowflake://{user}:{password}@{account_identifier}/{database}/{schema}>?warehouse={warehouse}&role={role}'
    

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

    def get_sql(self, params: Dict, optionalHeaders: Dict = None) -> str:
        schema = params['schema']
        table = params['tableName']
        database = params['cluster']
        
        sql = SnowflakePreviewClient.SQL_STATEMENT.format(database=database,
                                                          schema=schema,
                                                          table=table)

        return sql

    def get_conn_str(self, params: Dict, optionalHeaders: Dict = None)  -> str:
        schema = params['schema']
        database = params['cluster']
        
        conn_str = SnowflakePreviewClient.CONN_STR.format(
            user=self.username,
            password=self.password,
            account_identifier=self.account_identifier,
            database=database,
            schema=schema,
            warehouse=self.warehouse,
            role=self.role)

        return conn_str
