from flask import Request
from typing import Dict, Any
from amundsen_application.authz.actions.base import BaseAction
from amundsen_application.authz.mappers.base import BaseMapper
from amundsen_application.api.exceptions import AuthorizationMappingMissingException


class DefaultRequestToActionMapper(BaseMapper):
    """
    Reference implementation of mapper.
    Given request context, checks blueprint and function used to process the request
    and returns the corresponding action.
    """
    def __init__(self) -> None:
        self._mappings: Dict[str, Dict[str, BaseAction]] = {}

    def add_mapping(self, required_action: BaseAction, **kwargs: Any) -> None:
        if not "blueprint_name" in kwargs:
            raise Exception("Expected `blueprint_name` in keyword arguments")
        if not "function_name" in kwargs:
            raise Exception("Expected `function_name` in keyword arguments")

        blueprint_name = kwargs["blueprint_name"]
        function_name = kwargs["function_name"]
        self._mappings[blueprint_name] = self._mappings.get(blueprint_name, {})
        self._mappings[blueprint_name][function_name] = required_action

    def get_mapping(self, *, request: Request) -> BaseAction:
        if not request.endpoint:
            raise Exception(
                "Unexpected error: Request do not contain an endpoint"
            )
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
