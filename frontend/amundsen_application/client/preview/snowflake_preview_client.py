
import logging
import os
from typing import Dict,Tuple,Any  # noqa: F401
import json
from urllib.parse import quote_plus


from amundsen_application.client.preview.sqlalchemy_base_preview_client import SqlAlchemyBasePreviewClient

class SnowflakePreviewClient(SqlAlchemyBasePreviewClient):

    SQL_STATEMENT = 'SELECT * FROM {database}.{schema}.{table} LIMIT {limit};'
    CONN_STR = 'snowflake://{user}:{password}@{account_identifier}/{database}/{schema}'


    def __init__(self,) -> None:
        super().__init__()
        self.account_identifier = os.getenv("PREVIEW_CLIENT_SNOWFLAKE_ACCOUNT_IDENTIFIER")
        self.username = os.getenv("PREVIEW_CLIENT_SNOWFLAKE_USERNAME")
        self.password = quote_plus(os.getenv("PREVIEW_CLIENT_SNOWFLAKE_PASSWORD"))
        self.conn_args = os.getenv("PREVIEW_CLIENT_SNOWFLAKE_CONN_ARGS")
        if self.conn_args is None or self.conn_args == '':
            self.conn_args = {}
        if self.conn_args:
            self.conn_args = json.loads(self.conn_args)

        logging.info(f"account_identifier={self.account_identifier}")
        logging.info(f"username={self.username}")
        logging.info(f"conn_args={self.conn_args}")

    def _is_preview_client_configured(self) -> bool:
        return (self.account_identifier is not None and \
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
                                                          table=table,
                                                          limit=self.limit)

        return sql

    def get_conn_str(self, params: Dict, optionalHeaders: Dict = None)  -> Tuple[str,Dict[str,Any]]:
        schema = params['schema']
        database = params['cluster']

        conn_str = SnowflakePreviewClient.CONN_STR.format(
            user=self.username,
            password=self.password,
            account_identifier=self.account_identifier,
            database=database,
            schema=schema)

        return (conn_str,self.conn_args)
