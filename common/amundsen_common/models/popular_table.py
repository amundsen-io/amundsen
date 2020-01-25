from typing import Optional

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class PopularTable:
    database: str = attr.ib()
    cluster: str = attr.ib()
    schema: str = attr.ib()
    name: str = attr.ib()
    description: Optional[str] = None


class PopularTableSchema(AttrsSchema):
    class Meta:
        target = PopularTable
        register_as_scheme = True
