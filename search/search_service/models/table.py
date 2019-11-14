from marshmallow import Schema, fields, post_load
from typing import Any, Dict, Iterable, List, Optional, Set
from .base import Base


class Table(Base):
    TYPE = 'table'

    def __init__(self, *,
                 name: str,
                 key: str,
                 description: str,
                 cluster: str,
                 database: str,
                 schema_name: str,
                 column_names: Iterable[str],
                 column_descriptions: List[str] = [],
                 tags: Iterable[str],
                 last_updated_epoch: int,
                 display_name: Optional[str] = None,
                 total_usage: int = 0) -> None:
        self.name = name
        self.key = key
        self.description = description
        self.cluster = cluster
        self.database = database
        self.schema_name = schema_name
        self.column_names = column_names
        self.tags = tags
        self.last_updated_epoch = last_updated_epoch
        self.total_usage = total_usage
        self.column_descriptions = column_descriptions
        self.display_name = display_name

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
            'schema_name',
            'column_names',
            'tags',
            'last_updated_epoch',
            'display_name'
        }

    def __repr__(self) -> str:
        return 'Table(name={!r}, key={!r}, description={!r}, ' \
               'cluster={!r} database={!r}, schema_name={!r}, column_names={!r}, ' \
               'tags={!r}, last_updated={!r}, display_name={!r})'.format(self.name,
                                                                         self.key,
                                                                         self.description,
                                                                         self.cluster,
                                                                         self.database,
                                                                         self.schema_name,
                                                                         self.column_names,
                                                                         self.tags,
                                                                         self.last_updated_epoch,
                                                                         self.display_name)


class TableSchema(Schema):
    database = fields.Str()
    cluster = fields.Str()
    column_names = fields.List(fields.Str())
    schema_name = fields.Str()
    name = fields.Str()
    key = fields.Str()
    description = fields.Str()
    last_updated_epoch = fields.Str(allow_none=True)
    tags = fields.List(fields.Str())
    total_usage = fields.Int(allow_none=True)
    column_descriptions = fields.List(fields.Str(), allow_none=True)
    display_name = fields.Str(allow_none=True)

    @post_load
    def make(self, data: Dict[str, Any], **kwargs: Any) -> Table:
        return Table(**data)
