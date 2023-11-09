
from typing import Dict
import logging
import os
from http import HTTPStatus
from typing import Dict  # noqa: F401
import json

from openai import OpenAI

from flask import Response, jsonify, make_response

from amundsen_application.models.ai import GPTResponseSchema, GPTResponse, GPTMessage

LOGGER = logging.getLogger(__name__)


class GPTClient:

    def __init__(self,) -> None:
        self.client = OpenAI(
            # api_key defaults to os.environ.get("OPENAI_API_KEY")
            api_key=os.getenv("GPT_CLIENT_API_KEY")
        )
        # openai.api_key = os.getenv("GPT_CLIENT_API_KEY")
        self.model = os.getenv("GPT_CLIENT_API_MODEL")
        self.default_system_message = os.getenv("GPT_CLIENT_API_DEFAULT_SYSTEM_MESSAGE")

        LOGGER.info(f'default_system_message={self.default_system_message}')
        LOGGER.info(f'api_key={os.getenv("GPT_CLIENT_API_KEY")}')
        LOGGER.info(f'model={self.model}')

    def get_gpt_response(self, prompt: str) -> Response:
        response: Response = None

        LOGGER.info(f"prompt={prompt}")

        messages = []
        if self.default_system_message:
            messages.append({"role": "system", "content": self.default_system_message})
        messages.append({"role": "user", "content": prompt})

        # completion = openai.ChatCompletion.create(
        #     model=self.model,
        #     messages=messages
        # )
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        finish_reason = chat_completion.choices[0].finish_reason
        content = chat_completion.choices[0].message.content
        role = chat_completion.choices[0].message.role
        LOGGER.info(f"chat_completion={chat_completion}")
        LOGGER.info(f"finish_reason={finish_reason}")
        LOGGER.info(f"content={content}")
        LOGGER.info(f"role={role}")

        gpt_message = GPTMessage(content=content, role=role)
        gpt_response = GPTResponse(finish_reason=finish_reason, message=gpt_message)
        try:
            gpt_response_data = GPTResponseSchema().dump(gpt_response)
            LOGGER.info(f"gpt_response_data={gpt_response_data}")
            GPTResponseSchema().load(gpt_response_data)  # for validation only
            payload = json.dumps({'gpt_response': gpt_response_data}, default=str)
            LOGGER.info(f"payload={payload}")
            response =  make_response(payload, HTTPStatus.OK)
        except Exception as ex:
            LOGGER.exception('Error(s) occurred while building gpt response: ')
            payload = json.dumps({'gpt_response': {}}, default=str)
            response = make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)

        return response
