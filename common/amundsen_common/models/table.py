from typing import List, Optional

import attr

from amundsen_common.models.user import User
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class Reader:
    user: User
    read_count: int


class ReaderSchema(AttrsSchema):
    class Meta:
        target = Reader
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Tag:
    tag_type: str
    tag_name: str


class TagSchema(AttrsSchema):
    class Meta:
        target = Tag
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Watermark:
    watermark_type: Optional[str] = None
    partition_key: Optional[str] = None
    partition_value: Optional[str] = None
    create_time: Optional[str] = None


class WatermarkSchema(AttrsSchema):
    class Meta:
        target = Watermark
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Statistics:
    stat_type: str
    stat_val: Optional[str] = None
    start_epoch: Optional[int] = None
    end_epoch: Optional[int] = None


class StatisticsSchema(AttrsSchema):
    class Meta:
        target = Statistics
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Column:
    name: str
    description: Optional[str] = None
    col_type: str
    sort_order: int
    stats: List[Statistics] = []


class ColumnSchema(AttrsSchema):
    class Meta:
        target = Column
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Application:
    application_url: Optional[str] = None
    description: Optional[str] = None
    id: str
    name: Optional[str] = None
    kind: Optional[str] = None


class ApplicationSchema(AttrsSchema):
    class Meta:
        target = Application
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Source:
    source_type: str
    source: str


class SourceSchema(AttrsSchema):
    class Meta:
        target = Source
        register_as_scheme = True


# this is a temporary hack to satisfy mypy. Once https://github.com/python/mypy/issues/6136 is resolved, use
# `attr.converters.default_if_none(default=False)`
def default_if_none(arg: Optional[bool]) -> bool:
    return arg or False


@attr.s(auto_attribs=True, kw_only=True)
class ProgrammaticDescription:
    source: str
    text: str


class ProgrammaticDescriptionSchema(AttrsSchema):
    class Meta:
        target = ProgrammaticDescription
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class Table:
    database: str
    cluster: str
    schema: str
    name: str
    tags: List[Tag] = []
    badges: Optional[List[Tag]] = []
    table_readers: List[Reader] = []
    description: Optional[str] = None
    columns: List[Column]
    owners: List[User] = []
    watermarks: List[Watermark] = []
    table_writer: Optional[Application] = None
    last_updated_timestamp: Optional[int] = None
    source: Optional[Source] = None
    is_view: Optional[bool] = attr.ib(default=None, converter=default_if_none)
    programmatic_descriptions: List[ProgrammaticDescription] = []


class TableSchema(AttrsSchema):
    class Meta:
        target = Table
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class TableSummary:
    database: str = attr.ib()
    cluster: str = attr.ib()
    schema: str = attr.ib()
    name: str = attr.ib()
    description: Optional[str] = attr.ib(default=None)
    schema_description: Optional[str] = attr.ib(default=None)


class TableSummarySchema(AttrsSchema):
    class Meta:
        target = TableSummary
        register_as_scheme = True
