
from marshmallow import Schema, fields, EXCLUDE


class GPTMessage:
    def __init__(self, content: str = None, role: str = None) -> None:
        self.content = content
        self.role = role

class GPTMessageSchema(Schema):
    content = fields.Str()
    role = fields.Str()


class GPTResponse:
    def __init__(self, finish_reason: str = None, message: GPTMessage = None, error_text: str = '') -> None:
        self.finish_reason = finish_reason
        self.message = message
        self.error_text = error_text

class GPTResponseSchema(Schema):
    finish_reason = fields.Str()
    message = fields.Nested(GPTMessageSchema)
    error_text = fields.Str()
