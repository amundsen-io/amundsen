
from typing import Dict
import logging
from http import HTTPStatus
from typing import Dict  # noqa: F401

from flask import Response, jsonify, make_response

from amundsen_application.client.ai.gpt_client import GPTClient


class AIClient:

    def __init__(self,) -> None:
        self.gpt_client = GPTClient()

    def get_gpt_response(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        response: Response = self.gpt_client.get_gpt_response(params, optionalHeaders)

        return response
