# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Optional
from dataclasses import dataclass


@dataclass
class ResourceNotice:
    severity: int
    message: str
    details: dict
