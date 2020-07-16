# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0


from typing import Optional, Set, List

import attr
from amundsen_common.models.user import User as CommonUser
from marshmallow_annotations.ext.attrs import AttrsSchema

from .base import Base


@attr.s(auto_attribs=True, kw_only=True)
class User(Base, CommonUser):
    """
    This represents the part of a user stored in the search proxy
    """
    manager_email: Optional[str] = None

    def get_id(self) -> str:
        # uses the user email as the document id in ES
        return self.email if self.email else ''

    @classmethod
    def get_attrs(cls) -> Set:
        return {
            'full_name',
            'first_name',
            'last_name',
            'team_name',
            'email',
            'manager_email',
            'github_username',
            'is_active',
            'employee_type',
            'role_name',
        }

    @staticmethod
    def get_type() -> str:
        return 'user'


class UserSchema(AttrsSchema):
    class Meta:
        target = User
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchUserResult:
    total_results: int = attr.ib()
    results: List[User] = attr.ib(factory=list)


class SearchUserResultSchema(AttrsSchema):
    class Meta:
        target = SearchUserResult
        register_as_scheme = True
