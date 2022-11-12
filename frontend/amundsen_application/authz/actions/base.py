from enum import Enum
from typing import Type

class BaseAction(Enum):
    pass

def to_action(*, action_enum_cls: Type[BaseAction], label: str) -> Enum:
    return action_enum_cls[label.title()]

def to_label(*, action: BaseAction) -> str:
    return action.name.lower()
