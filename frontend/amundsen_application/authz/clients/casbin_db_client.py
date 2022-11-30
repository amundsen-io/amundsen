from amundsen_common.entity.resource_type import ResourceType, to_label as resource_type_to_label
from amundsen_application.authz.actions.base import BaseAction, to_label as action_to_label
from amundsen_application.authz.clients.base import BaseClient
from amundsen_common.models.user import User
import casbin_sqlalchemy_adapter
import casbin
import os
from sqlalchemy import create_engine

class CasbinDbClient(BaseClient):
    """
    WIP - Authorization Client that leverages Casbin as policy enforcer and persistent database as policy storage
    """

    def __init__(self) -> None:
        db_url = os.getenv("CASBIN_MODEL_DATABASE_ENGINE_URL")
        if db_url is None:
            raise Exception("Casbin Database URL not specified. set url as 'CASBIN_MODEL_DATABASE_ENGINE_URL' env variable")
        casbin_model_config_path = os.getenv("CASBIN_MODEL_CONFIG_PATH")
        if casbin_model_config_path is None:
            raise Exception("Casbin config file path not specified. Set path to the file as 'CASBIN_MODEL_CONFIG_PATH' env variable")

        self.engine = create_engine()
        self.adapter = casbin_sqlalchemy_adapter.Adapter(self.engine)
        self.enforcer = casbin.Enforcer(casbin_model_config_path, self.adapter)

    def is_authorized(self, *, user: User, object_type: ResourceType, object_id: str, action: BaseAction) -> bool:
        return self.enforcer.enforce(
            user.user_id, 
            resource_type_to_label(resource_type=object_type), 
            object_id, 
            action_to_label(action=action)
        )
