from typing import Dict

from marshmallow import Schema, fields, pre_load, post_load, validates_schema, ValidationError

from flask import Response, jsonify
from flask import current_app as app


"""
TODO: Explore all internationalization use cases and
redesign how User handles names
"""


class User:
    def __init__(self,
                 first_name: str = None,
                 last_name: str = None,
                 email: str = None,
                 display_name: str = None,
                 profile_url: str = None) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.display_name = display_name
        self.profile_url = profile_url

    def to_json(self) -> Response:
        user_info = dump_user(self)
        return jsonify(user_info)


class UserSchema(Schema):
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    display_name = fields.Str(required=True)
    profile_url = fields.Str(allow_none=True)

    @pre_load
    def generate_display_name(self, data: Dict) -> Dict:
        if data.get('display_name', None):
            return data

        if data.get('first_name', None) or data.get('last_name', None):
            data['display_name'] = "{} {}".format(data.get('first_name', ''), data.get('last_name', '')).strip()
            return data

        data['display_name'] = data.get('email', None)
        return data

    @pre_load
    def generate_profile_url(self, data: Dict) -> Dict:
        if data.get('profile_url', None):
            return data

        data['profile_url'] = ''
        if app.config['GET_PROFILE_URL']:
            data['profile_url'] = app.config['GET_PROFILE_URL'](data['display_name'])
        return data

    @post_load
    def make_user(self, data: Dict) -> User:
        return User(**data)

    @validates_schema
    def validate_user(self, data: Dict) -> None:
        if not data.get('display_name', None):
            raise ValidationError('One or more must be provided: "first_name", "last_name", "email", "display_name"')


def load_user(user_data: Dict) -> User:
    try:
        schema = UserSchema()
        data, errors = schema.load(user_data)
        return data
    except ValidationError as err:
        return err.messages


def dump_user(user: User) -> Dict:
    schema = UserSchema()
    try:
        data, errors = schema.dump(user)
        return data
    except ValidationError as err:
        return err.messages
