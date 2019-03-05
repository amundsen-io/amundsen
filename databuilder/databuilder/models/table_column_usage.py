from typing import Iterable, Union, Dict, Any, Iterator  # noqa: F401

from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, RELATION_START_KEY, RELATION_END_KEY,
    RELATION_START_LABEL, RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE
)
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.user import User
from databuilder.publisher.neo4j_csv_publisher import UNQUOTED_SUFFIX


class ColumnReader(object):
    """
    A class represent user's read action on column. Implicitly assumes that read count is one.
    """
    def __init__(self,
                 database,  # type: str
                 cluster,  # type: str
                 schema,  # type: str
                 table,  # type: str
                 column,  # type: str
                 user_email,  # type: str
                 read_count=1  # type: int
                 ):
        # type: (...) -> None
        self.database = database.lower()
        self.cluster = cluster.lower()
        self.schema = schema.lower()
        self.table = table.lower()
        self.column = column.lower()
        self.user_email = user_email.lower()
        self.read_count = read_count

    def __repr__(self):
        # type: () -> str
        return """\
ColumnReader(database={!r}, cluster={!r}, schema={!r}, table={!r}, column={!r}, user_email={!r}, read_count={!r})"""\
            .format(self.database, self.cluster, self.schema, self.table, self.column, self.user_email, self.read_count)


class TableColumnUsage(Neo4jCsvSerializable):
    """
    A model represents user <--> column graph model
    Currently it only support to serialize to table level
    """
    TABLE_NODE_LABEL = TableMetadata.TABLE_NODE_LABEL
    TABLE_NODE_KEY_FORMAT = TableMetadata.TABLE_KEY_FORMAT

    USER_TABLE_RELATION_TYPE = 'READ'
    TABLE_USER_RELATION_TYPE = 'READ_BY'

    # Property key for relationship read, readby relationship
    READ_RELATION_COUNT = 'read_count{}'.format(UNQUOTED_SUFFIX)

    def __init__(self,
                 col_readers,  # type: Iterable[ColumnReader]
                 ):
        # type: (...) -> None
        for col_reader in col_readers:
            if col_reader.column != '*':
                raise NotImplementedError('Column is not supported yet {}'.format(col_readers))

        self.col_readers = col_readers
        self._node_iterator = self._create_node_iterator()
        self._rel_iter = self._create_rel_iterator()

    def create_next_node(self):
        # type: () -> Union[Dict[str, Any], None]

        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_node_iterator(self):
        # type: () -> Iterator[Any]
        for col_reader in self.col_readers:
            if col_reader.column == '*':
                # using yield for better memory efficiency
                yield User(email=col_reader.user_email).create_nodes()[0]

    def create_next_relation(self):
        # type: () -> Union[Dict[str, Any], None]

        try:
            return next(self._rel_iter)
        except StopIteration:
            return None

    def _create_rel_iterator(self):
        # type: () -> Iterator[Any]
        for col_reader in self.col_readers:
            yield {
                RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
                RELATION_END_LABEL: User.USER_NODE_LABEL,
                RELATION_START_KEY: self._get_table_key(col_reader),
                RELATION_END_KEY: self._get_user_key(col_reader.user_email),
                RELATION_TYPE: TableColumnUsage.TABLE_USER_RELATION_TYPE,
                RELATION_REVERSE_TYPE: TableColumnUsage.USER_TABLE_RELATION_TYPE,
                TableColumnUsage.READ_RELATION_COUNT: col_reader.read_count
            }

    def _get_table_key(self, col_reader):
        # type: (ColumnReader) -> str
        return TableMetadata.TABLE_KEY_FORMAT.format(db=col_reader.database,
                                                     cluster=col_reader.cluster,
                                                     schema=col_reader.schema,
                                                     tbl=col_reader.table)

    def _get_user_key(self, email):
        # type: (str) -> str
        return User.get_user_model_key(email=email)

    def __repr__(self):
        # type: () -> str
        return 'TableColumnUsage(col_readers={!r})'.format(self.col_readers)
