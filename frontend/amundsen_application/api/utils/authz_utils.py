from flask import Request, current_app as app

from amundsen_common.entity.resource_type import ResourceType
from amundsen_common.models.user import User
from amundsen_application.authz.actions.base import BaseAction
from amundsen_application.authz.clients.base import BaseClient
from amundsen_application.authz.mappers.base import BaseMapper
from amundsen_application.api.exceptions import AuthorizationMappingMissingException
from typing import Optional

AUTHZ_CLIENT_INSTANCE = None

def get_authz_client() -> Optional[BaseClient]:
    global AUTHZ_CLIENT_INSTANCE
    if app.config["AUTHORIZATION_ENABLED"] and app.config["AUTHORIZATION_CLIENT_CLASS"] is None:
        raise Exception("Authorization client is not configured")
    if app.config["AUTHORIZATION_ENABLED"] and AUTHZ_CLIENT_INSTANCE is None:
        AUTHZ_CLIENT_INSTANCE = app.config["AUTHORIZATION_CLIENT_CLASS"]()

    return AUTHZ_CLIENT_INSTANCE


def get_required_action_from_request(request: Request) -> BaseAction:
    request_to_action_mapper: BaseMapper = app.config["AUTHORIZATION_REQUEST_TO_ACTION_MAPPER"]
    if app.config["AUTHORIZATION_ENABLED"] and request_to_action_mapper is None:
        raise Exception("Request to action mapping is not configured")

    return request_to_action_mapper.get_mapping(request=request)


def is_subject_authorized_to_perform_action_on_object(
    *, 
    user: User, 
    object_type: ResourceType, 
    object_id: str, 
    required_action: BaseAction) -> bool:
    is_authorized = False
    if app.config["AUTHORIZATION_ENABLED"] == False:
        is_authorized = True
        return is_authorized
    else:
        authz_client = get_authz_client()
        if authz_client is None:
            raise Exception("Can not get authorization client. Make sure that AUTHORIZATION_CLIENT_CLASS is set")
        try:
            is_authorized = authz_client.is_authorized(
                user=user, 
                object_type=object_type,
                object_id=object_id,
                action=required_action,
            )
        
        except AuthorizationMappingMissingException as e:
            is_authorized = app.config["AUTHORIZATION_ALLOW_ACCESS_ON_MISSING_MAPPING"]
    
    return is_authorized
