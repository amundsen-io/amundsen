# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional

import attr
from marshmallow3_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class Affinity:
    name: str
    strength: float
    key: str


class AffinitySchema(AttrsSchema):
    class Meta:
        target = Affinity
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Column:
    name: str
    col_type: str


class ColumnSchema(AttrsSchema):
    class Meta:
        target = Column
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Table:
    name: str
    columns: List[Column] = []
    affinities: List[Affinity] = []


class TableSchema(AttrsSchema):
    class Meta:
        target = Table
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Dataset:
    creatorUserMail: str
    key: str
    LastRefreshStatus: Optional[str] = None
    LastRefreshTime: Optional[str] = None
    RefreshScheduleDays: Optional[List[str]] = []
    RefreshScheduleTimes: Optional[List[str]] = []
    name: str
    tables: List[Table] = []


class DatasetSchema(AttrsSchema):
    class Meta:
        target = Dataset
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Report:
    createdBy: Optional[str] = None
    createdDateTime: Optional[str] = None
    key: str
    modifiedBy: Optional[str] = None
    modifiedDateTime: Optional[str] = None
    name: str
    reportType: Optional[str] = None
    datasets: List[Dataset] = []
    description: Optional[str] = None
    workspace: str
    source: str


class ReportSchema(AttrsSchema):
    class Meta:
        target = Report
        register_as_scheme = True

