from marshmallow import Schema, fields, post_dump
from marshmallow.exceptions import ValidationError

from typing import Dict, List


class Link:
    def __init__(self, label: str, href: str, target: str, use_router: bool) -> None:
        self.label = label
        self.href = href
        self.target = target
        """ Specify usage of React's built-in router vs a simple <a> anchor tag """
        self.use_router = use_router


class LinksSchema(Schema):
    label = fields.Str(required=True)
    href = fields.Str(required=True)
    target = fields.Str(required=False)
    use_router = fields.Bool(required=False)


class NavLinks:
    def __init__(self, links: List = []) -> None:
        self.links = links


class NavLinksSchema(Schema):
    links = fields.Nested(LinksSchema, many=True)

    @post_dump
    def validate_data(self, data: Dict) -> None:
        links = data.get('links', [])
        for link in links:
            if link.get('label') is None:
                raise ValidationError('All links must have a label')
            if link.get('href') is None:
                raise ValidationError('All links must have an href')
