# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class DashboardSummary:
    uri: str = attr.ib()
    cluster: str = attr.ib()
    group_name: str = attr.ib()
    group_url: str = attr.ib()
    product: str = attr.ib()
    name: str = attr.ib()
    url: str = attr.ib()
    description: Optional[str] = None
    last_successful_run_timestamp: Optional[int] = None


class DashboardSummarySchema(AttrsSchema):
    class Meta:
        target = DashboardSummary
        register_as_scheme = True

