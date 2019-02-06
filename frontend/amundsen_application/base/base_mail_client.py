import abc
from typing import List

from flask import Response


class BaseMailClient(abc.ABC):
    @abc.abstractmethod
    def __init__(self, recipients: List[str]) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def send_email(self, sender: str, recipients: List[str], subject: str, text: str, html: str) -> Response:
        raise NotImplementedError  # pragma: no cover
