# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import Dict

from flask import Response


class BaseDataFreshnessClient(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_freshness_data(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        """
        Returns a Response object, where the response data represents a json object
        with the freshness data accessible on 'freshness_data' key. The freshness data should
        match amundsen_application.models.preview_data.PreviewDataSchema
        """
        raise NotImplementedError  # pragma: no cover
