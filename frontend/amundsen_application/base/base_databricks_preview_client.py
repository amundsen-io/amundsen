# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
import logging
from databricks import sql

from flask import Response as FlaskResponse, make_response, jsonify
from http import HTTPStatus
from marshmallow import ValidationError
from requests import Response
from typing import Dict

from amundsen_application.base.base_preview_client import BasePreviewClient
from amundsen_application.models.preview_data import ColumnItem, PreviewData, PreviewDataSchema


class DatabricksPreviewClient(BasePreviewClient):
    def __init__(self) -> None:
        self.headers = {}

    def get_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        """
        Returns a FlaskResponse object, where the response data represents a json object
        with the preview data accessible on 'preview_data' key. The preview data should
        match amundsen_application.models.preview_data.PreviewDataSchema
        """
        logging.info("PreviewDataSchema params ")
        logging.info(params)
        try:
            # Clone headers so that it does not mutate instance's state
            headers = dict(self.headers)

            # Merge optionalHeaders into headers
            if optionalHeaders is not None:
                headers.update(optionalHeaders)

            # Request preview data
            table_name = f"{params['schema']}.{params['tableName']}"

            conn = sql.connect(
                server_hostname='adb-8116994530892803.3.azuredatabricks.net',
                http_path='sql/protocolv1/o/8116994530892803/1218-193400-vise273',
                access_token='dapi76a31261d0ae9b67a2153875a748e4fc')

            # Run a SQL query by using the preceding connection.
            cursor = conn.cursor()
            cursor.execute(f""" DESCRIBE TABLE {table_name} """)

            _columns = cursor.fetchall()

            cursor = conn.cursor()
            cursor.execute(f""" SELECT * FROM {table_name} LIMIT 10 """)

            column_names = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(column_names, row)))

            # Verify and return the results
            i = 0
            columns = []
            for c in _columns:
                if i < 7:
                    columns.append(ColumnItem(c[0], c[1]))
                i = i + 1
            preview_data = PreviewData(columns, results)
            try:
                data = PreviewDataSchema().dump(preview_data)
                PreviewDataSchema().load(data)  # for validation only
                payload = jsonify({'preview_data': data})
                return make_response(payload, HTTPStatus.OK)
            except ValidationError as err:
                logging.error("PreviewDataSchema serialization error " + str(err.messages))
                return make_response(jsonify({'preview_data': {}}), HTTPStatus.INTERNAL_SERVER_ERROR)
        except Exception as excpt:
            logging.error("PreviewDataSchema creation error " + str(excpt))
            return make_response(jsonify({'preview_data': {}}), HTTPStatus.INTERNAL_SERVER_ERROR)

    def get_feature_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> FlaskResponse:
        pass
