# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
import logging
from http import HTTPStatus
from typing import Dict

from amundsen_application.base.base_preview_client import BasePreviewClient
from amundsen_application.models.preview_data import (PreviewData,
                                                      PreviewDataSchema)
from flask import Response as FlaskResponse
from flask import jsonify, make_response
from marshmallow import ValidationError


class BaseS3PreviewClient(BasePreviewClient):
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def get_s3_preview_data(self, *, params: Dict) -> PreviewData:
        """
        Returns the data from S3 in PreviewData model format
        """
        pass  # pragma: no cover

    def get_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> FlaskResponse:
        try:
            preview_data = self.get_s3_preview_data(params=params)
            try:
                data = PreviewDataSchema().dump(preview_data)
                PreviewDataSchema().load(data)  # for validation only
                payload = jsonify({'preview_data': data})
                return make_response(payload, HTTPStatus.OK)
            except ValidationError as err:
                logging.error("PreviewDataSchema serialization error " + str(err.messages))
                return make_response(jsonify({'preview_data': {}}), HTTPStatus.INTERNAL_SERVER_ERROR)
        except Exception as err:
            logging.error("error getting s3 preview data " + str(err))
            return make_response(jsonify({'preview_data': {}}), HTTPStatus.INTERNAL_SERVER_ERROR)

    def get_feature_preview_data(self, params: Dict, optionalHeaders: Dict = None) -> FlaskResponse:
        """
        BaseS3PreviewClient only supports data preview currently but this function needs to be stubbed to
        implement the BasePreviewClient interface
        """
        pass
