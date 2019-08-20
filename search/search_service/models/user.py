from marshmallow import Schema, fields, post_load
from typing import Any, Dict, Set
from .base import Base


class User(Base):
    TYPE = 'user'

    def __init__(self, *,
                 first_name: str,
                 last_name: str,
                 name: str,
                 team_name: str,
                 email: str,
                 manager_email: str,
                 github_username: str,
                 is_active: bool,
                 employee_type: str) -> None:
        self.name = name
        self.first_name = first_name
        self.last_name = last_name
        self.team_name = team_name
        self.email = email
        self.manager_email = manager_email
        self.github_username = github_username
        self.is_active = is_active
        self.employee_type = employee_type

    def get_id(self) -> str:
        # uses the user email as the document id in ES
        return self.email

    @classmethod
    def get_attrs(cls) -> Set:
        return {
            'name',
            'first_name',
            'last_name',
            'team_name',
            'email',
            'manager_email',
            'github_username',
            'is_active',
            'employee_type'
        }

    def __repr__(self) -> str:
        return 'User(name={!r}, first_name={!r}, last_name={!r}, ' \
               'team_name={!r} email={!r}, manager_email={!r}, github_username={!r}, ' \
               'is_active={!r}, employee_type={!r})'.format(self.name,
                                                            self.first_name,
                                                            self.last_name,
                                                            self.team_name,
                                                            self.email,
                                                            self.manager_email,
                                                            self.github_username,
                                                            self.is_active,
                                                            self.employee_type)


class UserSchema(Schema):
    name = fields.Str(allow_none=True)
    email = fields.Str()
    is_active = fields.Boolean(allow_none=True)
    employee_type = fields.Str(allow_none=True)

    @post_load
    def make(self, data: Dict[str, Any], **kwargs: Any) -> User:
        return User(**data)
