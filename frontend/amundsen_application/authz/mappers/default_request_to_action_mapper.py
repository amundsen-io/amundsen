from flask import Request
from typing import Dict
from amundsen_application.authz.actions.base import BaseAction
from amundsen_application.authz.mappers.base import BaseMapper
from amundsen_application.api.exceptions import AuthorizationMappingMissingException


class DefaultRequestToActionMapper(BaseMapper):
    def __init__(self):
        self._mappings: Dict[str, Dict[str, BaseAction]] = {}

    def add_mapping(self, *, blueprint_name: str, function_name: str, required_action: BaseAction) -> None:
        self._mappings[blueprint_name] = self._mappings.get(blueprint_name, {})
        self._mappings[blueprint_name][function_name] = required_action

    def get_mapping(self, *, request: Request) -> BaseAction:
        blueprint_name, function_name = request.endpoint.split('.')
        if blueprint_name not in self._mappings:
            raise AuthorizationMappingMissingException(
                f'Authorization mapping not specified for blueprint {blueprint_name}'
            )
        if function_name not in self._mappings[blueprint_name]:
            raise AuthorizationMappingMissingException(
                f'Authorization mapping not specified for function {function_name} of blueprint {blueprint_name}'
            )
        return self._mappings[blueprint_name][function_name]
