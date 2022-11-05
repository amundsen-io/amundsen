from enum import Enum

class BaseAction(Enum):
    pass

def to_action(cls: BaseAction, *, label: str) -> Enum:
    return cls[label.title()]

def to_label(*, action: BaseAction) -> str:
    return action.name.lower()
