from amundsen_common.entity.resource_type import ResourceType
from amundsen_application.authz.actions.base import BaseAction
from amundsen_application.authz.clients.base import BaseClient
from amundsen_common.models.user import User


class CasbinClient(BaseClient):
    """
    Base Proxy, which behaves like an interface for all
    the proxy clients available in the amundsen metadata service
    """
    def __init__(self) -> None:
        pass

    def is_authorized(self, *, user: User, object_type: ResourceType, object_id: str, action: BaseAction) -> bool:
        pass
