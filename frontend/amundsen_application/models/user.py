from typing import Dict

from marshmallow import Schema, fields, pre_load, post_load, validates_schema, ValidationError

from flask import Response, jsonify
from flask import current_app as app


"""
TODO: Explore all internationalization use cases and
redesign how User handles names
"""


class User:
    # TODO: alphabetize after we have the real params
    def __init__(self,
                 first_name: str = None,
                 last_name: str = None,
                 email: str = None,
                 display_name: str = None,
                 profile_url: str = None,
                 user_id: str = None,
                 github_name: str = None,
                 is_active: bool = True,
                 manager_name: str = None,
                 role_name: str = None,
                 slack_url: str = None,
                 team_name: str = None) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.display_name = display_name
        self.profile_url = profile_url

        # TODO: modify the following names as needed after backend support is implemented
        self.user_id = user_id
        self.github_name = github_name
        self.is_active = is_active
        self.manager_name = manager_name
        self.role_name = role_name
        self.slack_url = slack_url
        self.team_name = team_name
        # TODO: frequent_used, bookmarked, & owned resources

    def to_json(self) -> Response:
        user_info = dump_user(self)
        return jsonify(user_info)


class UserSchema(Schema):
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    display_name = fields.Str(required=True)
    profile_url = fields.Str(allow_none=True)

    user_id = fields.Str(required=True)
    github_name = fields.Str(allow_none=True)
    is_active = fields.Bool(allow_none=True)
    manager_name = fields.Str(allow_none=True)
    role_name = fields.Str(allow_none=True)
    slack_url = fields.Str(allow_none=True)
    team_name = fields.Str(allow_none=True)

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
        if not data.get('user_id', None):
            raise ValidationError('"user_id" must be provided')


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
