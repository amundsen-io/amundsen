# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import requests
import uuid
import json

from requests import Response
from typing import Any, Dict  # noqa: F401

from amundsen_application.base.base_superset_preview_client import BaseSupersetPreviewClient

# 'main' is an existing default Superset database which serves for demo purposes
DEFAULT_DATABASE_MAP = {
    'postgres': 1,
}

AUTH_URL = 'http://superset:8088/api/v1/security/login'
CSRF_URL = 'http://superset:8088/api/v1/security/csrf_token/'
DEFAULT_URL = 'http://superset:8088/superset/sql_json/'

class SupersetPreviewClient(BaseSupersetPreviewClient):
    def __init__(self,
                 *,
                 database_map: Dict[str, int] = DEFAULT_DATABASE_MAP,
                 url: str = DEFAULT_URL) -> None:
        self.database_map = database_map
        self.headers = {}        
        self.url = url

    def authenticate(self) -> None:
        try:
            logging.info('Authenticating with apache superset')

            rsp = requests.post(AUTH_URL, json=dict(username='salt', password='salt', provider='db'))   

            access_token = rsp.json()['access_token']

            self.headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=utf-8',
                'Referer': AUTH_URL
            }        
        except Exception as e:
            logging.error('Encountered error authenticating with apache superset: ' + str(e))            

    def post_to_sql_json(self, *, params: Dict, headers: Dict) -> Response:
        """
        Returns the post response from Superset's `sql_json` endpoint
        """

        logging.info(params)

        # Create the appropriate request data
        try:
            request_data = {}  # type: Dict[str, Any]

            # Superset's sql_json endpoint requires a unique client_id
            request_data['client_id'] = str(uuid.uuid4())

            # Superset's sql_json endpoint requires the id of the database that it will execute the query on
            database_name = params.get('database')
            request_data['database_id'] = self.database_map.get(database_name, '')

            # Generate the sql query for the desired data preview content
            try:
                # 'main' is an existing default Superset schema which serves for demo purposes
                schema = params.get('schema')

                # 'ab_role' is an existing default Superset table which serves for demo purposes
                table_name = params.get('tableName')

                request_data['sql'] = 'SELECT * FROM {schema}.{table} LIMIT 50'.format(schema=schema, table=table_name)
            except Exception as e:
                logging.error('Encountered error generating request sql: ' + str(e))
        except Exception as e:
            logging.error('Encountered error generating request data: ' + str(e))

        self.authenticate()

        logging.info(self.headers)

        # Post request to Superset's `sql_json` endpoint
        rsp = requests.post(self.url, data=json.dumps(request_data), headers=self.headers)

        logging.info(rsp)
        logging.info(rsp.json())

        return rsp

