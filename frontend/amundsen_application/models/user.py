from typing import Dict

from amundsen_common.models.user import UserSchema, User
from flask import current_app as app
from marshmallow import ValidationError


def load_user(user_data: Dict) -> User:
    try:
        schema = UserSchema()
        # To make sure we pass frontend configuration to amundsen common models
        user_data['GET_PROFILE_URL'] = app.config['GET_PROFILE_URL']
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
