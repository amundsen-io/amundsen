from abc import ABCMeta, abstractmethod
from amundsen_application.authz.actions.base import BaseAction
from typing import Dict, Any
from flask import Request

class BaseMapper(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self) -> None:
        self._mappings: Dict[Any, Any] = {}

    @abstractmethod
    def add_mapping(self, required_action: BaseAction, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def get_mapping(self, *, request: Request) -> BaseAction:
        pass
