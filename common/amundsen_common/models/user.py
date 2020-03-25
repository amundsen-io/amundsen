from typing import Optional

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class User:
    # ToDo (Verdan): Make ID a required field.
    #  In case if there is only email, id could be email.
    #  All the transactions and communication will be handled by ID
    id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    github_username: Optional[str] = None
    team_name: Optional[str] = None
    slack_id: Optional[str] = None
    employee_type: Optional[str] = None
    manager_fullname: Optional[str] = None
    role_name: Optional[str] = None


class UserSchema(AttrsSchema):
    class Meta:
        target = User
        register_as_scheme = True
