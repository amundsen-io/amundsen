import abc
from typing import Dict, List

from flask import Response


class BaseMailClient(abc.ABC):
    @abc.abstractmethod
    def __init__(self, recipients: List[str]) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def send_email(self,
                   sender: str,
                   recipients: List[str],
                   subject: str,
                   text: str,
                   html: str,
                   optional_data: Dict) -> Response:
        """
        Sends an email using the following parameters
        :param sender: The sending address associated with the email
        :param recipients: A list of receipients for the email
        :param subject: The subject of the email
        :param text: Plain text email content
        :param html: HTML email content
        :param optional_data: A dictionary of any values needed for custom implementations
        :return:
        """
        raise NotImplementedError  # pragma: no cover
