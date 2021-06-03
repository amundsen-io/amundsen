from typing import Optional

import attr

from marshmallow3_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class Query:
    name: Optional[str]
    text: str
    url: Optional[str]


class QuerySchema(AttrsSchema):
    class Meta:
        target = Query
        register_as_scheme = True
