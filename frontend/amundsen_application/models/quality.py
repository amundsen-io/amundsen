# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

import attr
from marshmallow3_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class TableQualityChecksSummary:
    num_checks_success: int = attr.ib()
    num_checks_failed: int = attr.ib()
    num_checks_total: int = attr.ib()
    external_url: str = attr.ib()
    last_run_timestamp: Optional[int] = attr.ib()


class TableQualityChecksSchema(AttrsSchema):
    class Meta:
        target = TableQualityChecksSummary
        register_as_schema = True
