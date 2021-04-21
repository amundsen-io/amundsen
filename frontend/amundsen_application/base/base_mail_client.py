# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import Dict, List

from flask import Response


class BaseMailClient(abc.ABC):
    @abc.abstractmethod
    def __init__(self, recipients: List[str]) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def send_email(self,
                   html: str,
                   subject: str,
                   optional_data: Dict,
                   recipients: List[str],
                   sender: str) -> Response:
        """
        Sends an email using the following parameters
        :param html: HTML email content
        :param subject: The subject of the email
        :param optional_data: A dictionary of any values needed for custom implementations
        :param recipients: A list of recipients for the email
        :param sender: The sending address associated with the email
        :return:
        """
        raise NotImplementedError  # pragma: no cover
