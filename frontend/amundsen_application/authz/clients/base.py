from abc import ABCMeta, abstractmethod
from amundsen_common.models.user import User
from amundsen_common.entity.resource_type import ResourceType
from amundsen_application.authz.actions.base import (BaseAction)

from enum import Enum, auto


class BaseClient(metaclass=ABCMeta):
    """
    Base Client, which behaves like an interface for all
    """

    @abstractmethod
    def is_authorized(self, *, user: User, object_type: ResourceType, object_id: str, action: BaseAction) -> bool:
        pass

    """
    TODO - different methods - get_user_permissions, get_authorized_users, filter_search_request
    """
