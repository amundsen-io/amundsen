# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass


@dataclass
class ResourceNotice:
    """
    An object representing a notice to be displayed about a particular data resource (e.g. table or dashboard).
    """
    severity: int
    message: str
    details: dict
