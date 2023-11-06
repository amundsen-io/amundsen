
from typing import Dict
import logging
import os
from http import HTTPStatus
from typing import Dict  # noqa: F401

import openai

from flask import Response, jsonify, make_response

from amundsen_application.models.ai import GPTResponseSchema, GPTResponse, GPTMessage


class GPTClient:

    def __init__(self,) -> None:
        openai.api_key = os.getenv("GPT_CLIENT_API_KEY")
        self.model = os.getenv("GPT_CLIENT_API_MODEL")
        self.default_system_message = os.getenv("GPT_CLIENT_API_DEFAULT_SYSTEM_MESSAGE")

        logging.info(f'api_key={os.getenv("GPT_CLIENT_API_KEY")}')

    def get_gpt_response(self, params: Dict, optionalHeaders: Dict = None) -> Response:
        response: Response = None

        messages = []
        if self.default_system_message:
            messages.append({"role": "system", "content": self.default_system_message})
        messages.append({"role": "user", "content": params["prompt"]})

        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )

        GPTResponse
        rows = [dict(zip(col_names, row)) for row in result]
        column_metadata = [ColumnItem(n, t) for n, t in zip(col_names, col_types)]

        completion['choices'][0]['message']['content']
        gpt_message = GPTMessage(content=completion['choices'][0]['message']['content'], role=completion['choices'][0]['message']['role'])
        gpt_response = GPTResponse(finish_reason=completion['choices'][0]['finish_reason'], gpt_message=gpt_message)
        try:
            gpt_response_data = GPTResponseSchema().dump(gpt_response)
            GPTResponseSchema().load(gpt_response_data)  # for validation only
            payload = json.dumps({'gpt_response': gpt_response_data}, default=str)
            response =  make_response(payload, HTTPStatus.OK)
        except ValidationError as err:
            logging.exception('Error(s) occurred while building gpt response: ')
            payload = json.dumps({'gpt_response': {}}, default=str)
            response = make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)

        return response


    def is_supported_preview_source(self, params: Dict, optionalHeaders: Dict = None) -> bool:
        pass