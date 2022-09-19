import attr
from typing import List, Optional
from marshmallow3_annotations.ext.attrs import AttrsSchema

from metadata_service.entity.attribute import Attribute




@attr.s(auto_attribs=True, kw_only=True)
class AppEvents:
    key: str
    name: str
    created_timestamp: Optional[int]
    last_updated_timestamp: Optional[int]
    description: Optional[str] = attr.ib(default=None)
    owned_by: Optional[str] = attr.ib(default=None)
    label: Optional[str] = attr.ib(default=None)
    action: Optional[str] = attr.ib(default=None)
    category: Optional[str] = attr.ib(default=None)
    source: Optional[str] = attr.ib(default=None)
    vertical: Optional[str] = attr.ib(default=None)
    attributes: List[Attribute] = []


class AppEventsSchema(AttrsSchema):
    class Meta:
        target = AppEvents
        register_as_scheme = True
