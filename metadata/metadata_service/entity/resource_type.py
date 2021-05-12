# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum, auto


class ResourceType(Enum):
    Table = auto()
    Dashboard = auto()
    User = auto()
    Column = auto()


def to_resource_type(*, label: str) -> ResourceType:
    return ResourceType[label.title()]
