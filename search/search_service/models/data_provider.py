# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import time
from typing import (
    List, Optional, Set,
)

import attr
from marshmallow3_annotations.ext.attrs import AttrsSchema

from search_service.models.base import Base
from search_service.models.tag import Tag


@attr.s(auto_attribs=True, kw_only=True)
class DataProvider(Base):
    """
    This represents the part of a file stored in the search proxy
    """
    id: str
    name: str
    key: str
    description: str
    data_channel_names: List[str]
    data_channel_types: List[str]
    data_channel_descriptions: List[str]
    data_location_names: List[str]
    data_location_types: List[str]
    display_name: Optional[str] = None
    tags: Optional[List[Tag]] = None
    badges: Optional[List[Tag]] = None
    description: Optional[str] = None
    last_updated_timestamp: int = int(time.time())
    programmatic_descriptions: Optional[List[str]] = None

    def get_id(self) -> str:
        return self.id

    def get_attrs_dict(self) -> dict:
        attrs_dict = self.__dict__.copy()
        if self.tags is not None:
            attrs_dict['tags'] = [str(tag) for tag in self.tags]
        else:
            attrs_dict['tags'] = None
        if self.badges is not None:
            attrs_dict['badges'] = [str(badge) for badge in self.badges]
        else:
            attrs_dict['badges'] = None
        return attrs_dict

    @classmethod
    def get_attrs(cls) -> Set:
        return {
            'id',
            'name',
            'key',
            'description',
            'data_channel_names',
            'data_channel_types',
            'data_channel_descriptions',
            'data_location_names',
            'data_location_types',
            'tags',
            'badges',
            'last_updated_timestamp',
            'display_name',
        }

    @staticmethod
    def get_type() -> str:
        return 'data_provider'


class SearchDataProviderSchema(AttrsSchema):
    class Meta:
        target = DataProvider
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchDataProviderResult:
    total_results: int = attr.ib()
    results: List[DataProvider] = attr.ib(factory=list)


class SearchDataProviderResultSchema(AttrsSchema):
    class Meta:
        target = SearchDataProviderResult
        register_as_scheme = True
