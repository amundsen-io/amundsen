from amundsen_application.authz.actions.base import BaseAction
from enum import auto

class RWAction(BaseAction):
    READ = auto()
    WRITE = auto()
