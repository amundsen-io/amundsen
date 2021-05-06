from typing import List, Optional

import attr

from amundsen_common.models.user import User
from amundsen_common.models.badge import Badge
from amundsen_common.models.tag import Tag
from amundsen_common.models.table import Column, Stat, ProgrammaticDescription, Watermark
from amundsen_common.models.dashboard import Query
from marshmallow3_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class Feature:
   key: Optional[str] = attr.ib(default=None)
   name: str
   version: str  # ex: "1.2.0"
   status: str
   feature_group: str
   entity: Optional[List[str]]
   data_type: Optional[str]
   availability: List[str]
   description: Optional[str] = attr.ib(default=None)
   owners: List[User]
   badges: List[Badge]
   owner_tags: Optional[List[Tag]] # non editable
   tags: List[Tag] # editable
   generation_code: Optional[Query]
   programmatic_descriptions: List[ProgrammaticDescription] 
   watermarks: List[Watermark]
   stats: List[Stat]
   last_updated_timestamp: Optional[int]
   created_timestamp: Optional[int]
   partition_column: Optional[Column]


class FeatureSchema(AttrsSchema):
    class Meta:
        target = Feature
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class FeatureSummary:
   key: str  # ex: test_feature_group_name/test_feature_name/1.2.0
   name: str
   version: str
   availability: List[str]
   entity: Optional[List[str]] = attr.ib(default=[])
   description: Optional[str] = attr.ib(default=None)
   badges: List[Badge]
   last_updated_timestamp: Optional[int]


class FeatureSummarySchema(AttrsSchema):
    class Meta:
        target = FeatureSummary
        register_as_scheme = True
