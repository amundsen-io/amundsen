from amundsen_common.entity.resource_type import ResourceType, to_label as resource_type_to_label
from amundsen_application.authz.actions.base import BaseAction, to_label as action_to_label
from amundsen_application.authz.clients.base import BaseClient
from amundsen_common.models.user import User
import casbin
import os
import sys
import inspect

class CasbinExampleCsvClient(BaseClient):
    """
    Example implementation of Authorization Client using Casbin
    """

    def __init__(self) -> None:
        script_dir = os.path.dirname(inspect.getfile(CasbinExampleCsvClient))
        base_path = os.path.join(script_dir, "casbin_example_csv_client")
        policy_file = os.path.join(base_path, "policy.csv")
        model_file = os.path.join(base_path, "model.conf")
        self.enforcer = casbin.Enforcer(model_file, policy_file)

    def is_authorized(self, *, user: User, object_type: ResourceType, object_id: str, action: BaseAction) -> bool:
        return self.enforcer.enforce(
            user.user_id, 
            resource_type_to_label(resource_type=object_type), 
            object_id, 
            action_to_label(action=action)
        )
