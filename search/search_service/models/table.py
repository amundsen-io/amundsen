from typing import List, Optional, Set

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema

from .base import Base


@attr.s(auto_attribs=True, kw_only=True)
class Table(Base):
    """
    This represents the part of a table stored in the search proxy
    """
    database: str
    cluster: str
    schema: str
    name: str
    key: str
    display_name: Optional[str] = None
    tags: List[str]
    description: Optional[str] = None
    last_updated_timestamp: int
    # The following properties are lightly-transformed properties from the normal table object:
    column_names: List[str]
    column_descriptions: List[str] = []
    # The following are search-only properties:
    total_usage: int = 0

    def get_id(self) -> str:
        # uses the table key as the document id in ES
        return self.key

    @classmethod
    def get_attrs(cls) -> Set:
        return {
            'name',
            'key',
            'description',
            'cluster',
            'database',
            'schema',
            'column_names',
            'tags',
            'last_updated_timestamp',
            'display_name'
        }

    @staticmethod
    def get_type() -> str:
        return 'table'


class TableSchema(AttrsSchema):
    class Meta:
        target = Table
        register_as_scheme = True
