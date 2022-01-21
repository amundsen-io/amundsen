# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class Resource(Enum):
    TABLE = 0
    DASHBOARD = 1
    FEATURE = 2
    USER = 3


RESOURCE_STR_MAPPING = {
    'table': Resource.TABLE,
    'dashboard': Resource.DASHBOARD,
    'feature': Resource.FEATURE,
    'user': Resource.USER,
}


def get_index_for_resource(resource_type: Resource) -> str:
    resource_str = resource_type.name.lower()
    return f"{resource_str}_search_index"
