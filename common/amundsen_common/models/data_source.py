# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional

import attr

from amundsen_common.models.badge import Badge
from amundsen_common.models.tag import Tag
from marshmallow3_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class DataLocation:
    name: str
    key: Optional[str] = None
    type: Optional[str] = None


class DataLocationSchema(AttrsSchema):
    class Meta:
        target = DataLocation
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class FilesystemDataLocation(DataLocation):
    drive: Optional[str] = None


class FilesystemDataLocationSchema(AttrsSchema):
    class Meta:
        target = FilesystemDataLocation
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class AwsS3DataLocation(DataLocation):
    bucket: Optional[str] = None


class AwsS3DataLocationSchema(AttrsSchema):
    class Meta:
        target = AwsS3DataLocation
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class DataChannel:
    name: str
    key: Optional[str] = None
    description: Optional[str] = None
    license: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    data_locations: Optional[List[DataLocation]]


class DataChannelSchema(AttrsSchema):
    class Meta:
        target = DataChannel
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class DataProvider:
    name: str
    key: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    data_channels: List[DataChannel]
    # tags: List[Tag] = []
    # badges: List[Badge] = []


class DataProviderSchema(AttrsSchema):
    class Meta:
        target = DataProvider
        register_as_scheme = True

@attr.s(auto_attribs=True, kw_only=True)
class File:
    name: str
    key: Optional[str] = None
    description: Optional[str] = None
    type: str = None
    path: str = None
    is_directory: bool = None
    data_location: Optional[DataLocation] = None
    data_channel: Optional[DataChannel] = None
    data_provider: Optional[DataProvider] = None
    # tags: List[Tag] = []
    # badges: List[Badge] = []


class FileSchema(AttrsSchema):
    class Meta:
        target = File
        register_as_scheme = True


# this is a temporary hack to satisfy mypy. Once https://github.com/python/mypy/issues/6136 is resolved, use
# `attr.converters.default_if_none(default=False)`
def default_if_none(arg: Optional[bool]) -> bool:
    return arg or False
