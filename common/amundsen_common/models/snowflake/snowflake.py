# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, List

import attr

from marshmallow3_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class SnowflakeListing:
    global_name: str
    name: str
    title: Optional[str]
    subtitle: Optional[str]
    description: Optional[str]


class SnowflakeListingSchema(AttrsSchema):
    class Meta:
        target = SnowflakeListing
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SnowflakeTableShare:
    owner_account: str
    name: str
    listing: Optional[SnowflakeListing] = None


class SnowflakeTableShareSchema(AttrsSchema):
    class Meta:
        target = SnowflakeTableShare
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SnowflakeTableShares:
    snowflake_table_shares: Optional[List[SnowflakeTableShare]] = []


class SnowflakeTableSharesSchema(AttrsSchema):
    class Meta:
        target = SnowflakeTableShares
        register_as_scheme = True


# this is a temporary hack to satisfy mypy. Once https://github.com/python/mypy/issues/6136 is resolved, use
# `attr.converters.default_if_none(default=False)`
def default_if_none(arg: Optional[bool]) -> bool:
    return arg or False
