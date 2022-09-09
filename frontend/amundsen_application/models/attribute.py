import attr
from marshmallow3_annotations.ext.attrs import AttrsSchema

@attr.s(auto_attribs=True, kw_only=True)
class Attribute:
    name: str
    description: str
    
class AttributeSchema(AttrsSchema):
    class Meta:
        target = Attribute
        register_as_scheme = True
