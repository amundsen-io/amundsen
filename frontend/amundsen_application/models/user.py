from typing import Dict, Optional

from marshmallow import Schema, fields, pre_load, post_load, validates_schema, ValidationError

from flask import current_app as app


"""
TODO: Explore all internationalization use cases and
redesign how User handles names
"""


class User:
    def __init__(self,
                 display_name: str = None,
                 email: str = None,
                 employee_type: str = None,
                 first_name: str = None,
                 full_name: str = None,
                 github_username: str = None,
                 is_active: bool = True,
                 last_name: str = None,
                 manager_fullname: str = None,
                 profile_url: str = None,
                 role_name: str = None,
                 slack_id: str = None,
                 team_name: str = None,
                 user_id: str = None) -> None:
        self.display_name = display_name
        self.email = email
        self.employee_type = employee_type
        self.first_name = first_name
        self.full_name = full_name
        self.github_username = github_username
        self.is_active = is_active
        self.last_name = last_name
        self.manager_fullname = manager_fullname
        self.profile_url = profile_url
        self.role_name = role_name
        self.slack_id = slack_id
        self.team_name = team_name
        self.user_id = user_id
        # TODO: Add frequent_used, bookmarked, & owned resources


class UserSchema(Schema):
    display_name = fields.Str(allow_none=False)
    email = fields.Str(required=True)
    employee_type = fields.Str(allow_none=True)
    first_name = fields.Str(allow_none=True)
    full_name = fields.Str(allow_none=True)
    github_username = fields.Str(allow_none=True)
    is_active = fields.Bool(allow_none=True)
    last_name = fields.Str(allow_none=True)
    manager_fullname = fields.Str(allow_none=True)
    profile_url = fields.Str(allow_none=True)
    role_name = fields.Str(allow_none=True)
    slack_id = fields.Str(allow_none=True)
    team_name = fields.Str(allow_none=True)
    user_id = fields.Str(allow_none=False)

    def _str_no_value(self, s: Optional[str]) -> bool:
        # Returns True if the given string is None or empty
        if not s:
            return True
        if len(s.strip()) == 0:
            return True
        return False

    @pre_load
    def preprocess_data(self, data: Dict) -> Dict:
        if self._str_no_value(data.get('user_id')):
            data['user_id'] = data.get('email')

        if self._str_no_value(data.get('profile_url')):
            data['profile_url'] = ''
            if app.config['GET_PROFILE_URL']:
                data['profile_url'] = app.config['GET_PROFILE_URL'](data['user_id'])

        if self. _str_no_value(data.get('display_name')):
            if self._str_no_value(data.get('full_name')):
                data['display_name'] = data.get('email')
            else:
                data['display_name'] = data.get('full_name')

        return data

    @post_load
    def make_user(self, data: Dict) -> User:
        return User(**data)

    @validates_schema
    def validate_user(self, data: Dict) -> None:
        if self._str_no_value(data.get('display_name')):
            raise ValidationError('"display_name", "full_name", or "email" must be provided')

        if self._str_no_value(data.get('user_id')):
            raise ValidationError('"user_id" or "email" must be provided')


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
