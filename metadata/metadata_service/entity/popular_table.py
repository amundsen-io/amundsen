from typing import Optional


class PopularTable:

    def __init__(self, *,
                 database: str,
                 cluster: str,
                 schema: str,
                 name: str,
                 description: Optional[str] = None) -> None:
        self.database = database
        self.cluster = cluster
        self.schema = schema
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return """Table(database={!r}, cluster={!r}, schema={!r}, name={!r}, description={!r})"""\
            .format(self.database, self.cluster,
                    self.schema, self.name, self.description)
