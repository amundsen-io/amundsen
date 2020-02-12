from typing import Optional

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class User:
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    github_username: Optional[str] = None
    team_name: Optional[str] = None
    slack_id: Optional[str] = None
    employee_type: Optional[str] = None
    manager_fullname: Optional[str] = None


class UserSchema(AttrsSchema):
    class Meta:
        target = User
        register_as_scheme = True
