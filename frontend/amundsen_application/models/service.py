import attr
from typing import List, Optional
from marshmallow3_annotations.ext.attrs import AttrsSchema

from amundsen_application.models.attribute import Attribute
@attr.s(auto_attribs=True, kw_only=True)
class Service:
    key: str
    name: str
    created_timestamp: Optional[int]
    attributes: List[Attribute] = []
    last_updated_timestamp: Optional[int]
    stack: Optional[str] = attr.ib(default=None)
    owned_by: Optional[str] = attr.ib(default=None)
    git_repo: Optional[str] = attr.ib(default=None)
    victor_ops: Optional[str] = attr.ib(default=None)
    description: Optional[str] = attr.ib(default=None)
    criticality: Optional[str] = attr.ib(default=None)


class ServiceSchema(AttrsSchema):
    class Meta:
        target = Service
        register_as_scheme = True
