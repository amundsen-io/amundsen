# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from abc import ABC
from abc import abstractmethod
from flask import Response


class BaseNoticeClient(ABC):
    """
    Abstract interface for a client that provides alerts affecting a given table.
    """

    @abstractmethod
    def get_table_notices_summary(self, *, table_key: str) -> Response:
        """
        Returns table alerts response for a given table URI
        :param table_key: Table key for table to get alerts for
        :return: flask Response object
        """
        raise NotImplementedError
