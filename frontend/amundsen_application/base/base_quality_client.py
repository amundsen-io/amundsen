# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from abc import ABCMeta, abstractmethod
from flask import Response


class BaseQualityClient(metaclass=ABCMeta):
    """
    An abstract interface for a Quality Service Client
    """

    @abstractmethod
    def get_table_quality_checks_summary(self, *, table_key: str) -> Response:
        """
        Returns table quality checks for a given table uri
        :param table_key: Table key for the table whose table quality
        :return: TableQualityChecks object
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_table_quality_checks(self, *, table_key: str) -> bytes:
        """
        Returns table quality checks for a given table uri
        :param table_key: Table key for the table whose table quality
        :return: TableQualityChecks object
        """
        raise NotImplementedError  # pragma: no cover
