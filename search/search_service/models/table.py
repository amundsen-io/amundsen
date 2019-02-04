from typing import Iterable


class Table:
    def __init__(self, *,
                 name: str,
                 key: str,
                 description: str,
                 cluster: str,
                 database: str,
                 schema_name: str,
                 column_names: Iterable[str],
                 tags: Iterable[str],
                 last_updated_epoch: int) -> None:
        self.name = name
        self.key = key
        self.description = description
        self.cluster = cluster
        self.database = database
        self.schema_name = schema_name
        self.column_names = column_names
        self.tags = tags
        self.last_updated_epoch = last_updated_epoch

    def __repr__(self) -> str:
        return 'Table(name={!r}, key={!r}, description={!r}, ' \
               'cluster={!r} database={!r}, schema_name={!r}, column_names={!r}, ' \
               'tags={!r}, last_updated={!r})'.format(self.name,
                                                      self.key,
                                                      self.description,
                                                      self.cluster,
                                                      self.database,
                                                      self.schema_name,
                                                      self.column_names,
                                                      self.tags,
                                                      self.last_updated_epoch)
