from collections import namedtuple

from typing import Iterable, Any, Union, Iterator, Dict, Set  # noqa: F401

from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, NODE_LABEL, NODE_KEY, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)
from databuilder.publisher.neo4j_csv_publisher import UNQUOTED_SUFFIX

DESCRIPTION_NODE_LABEL = 'Description'


class ColumnMetadata:
    COLUMN_NODE_LABEL = 'Column'
    COLUMN_KEY_FORMAT = '{db}://{cluster}.{schema}/{tbl}/{col}'
    COLUMN_NAME = 'name'
    COLUMN_TYPE = 'type'
    COLUMN_ORDER = 'sort_order'
    COLUMN_DESCRIPTION = 'description'
    COLUMN_DESCRIPTION_FORMAT = '{db}://{cluster}.{schema}/{tbl}/{col}/_description'

    # pair of nodes makes relationship where name of variable represents order of relationship.
    COL_DESCRIPTION_RELATION_TYPE = 'DESCRIPTION'
    DESCRIPTION_COL_RELATION_TYPE = 'DESCRIPTION_OF'

    def __init__(self,
                 name,  # type: str
                 description,  # type: Union[str, None]
                 col_type,  # type: str
                 sort_order,  # type: int
                 ):
        # type: (...) -> None
        """
        TODO: Add stats
        :param name:
        :param description:
        :param col_type:
        :param sort_order:
        """
        self.name = name
        self.description = description
        self.type = col_type
        self.sort_order = sort_order

    def __repr__(self):
        # type: () -> str
        return 'ColumnMetadata({!r}, {!r}, {!r}, {!r})'.format(self.name,
                                                               self.description,
                                                               self.type,
                                                               self.sort_order)


# Tuples for de-dupe purpose on Database, Cluster, Schema. See TableMetadata docstring for more information
NodeTuple = namedtuple('KeyName', ['key', 'name', 'label'])
RelTuple = namedtuple('RelKeys', ['start_label', 'end_label', 'start_key', 'end_key', 'type', 'reverse_type'])


class TableMetadata(Neo4jCsvSerializable):
    """
    Table metadata that contains columns. It implements Neo4jCsvSerializable so that it can be serialized to produce
    Table, Column and relation of those along with relationship with table and schema. Additionally, it will create
    Database, Cluster, and Schema with relastionships between those.
    These are being created here as it does not make much sense to have different extraction to produce this. As
    database, cluster, schema would be very repititive with low cardinality, it will perform de-dupe so that publisher
    won't need to publish same nodes, relationships.

    This class can be used for both table and view metadata. If it is a View, is_view=True should be passed in.
    """
    TABLE_NODE_LABEL = 'Table'
    TABLE_KEY_FORMAT = '{db}://{cluster}.{schema}/{tbl}'
    TABLE_NAME = 'name'
    IS_VIEW = 'is_view{}'.format(UNQUOTED_SUFFIX)  # bool value needs to be unquoted when publish to neo4j

    TABLE_DESCRIPTION = 'description'
    TABLE_DESCRIPTION_FORMAT = '{db}://{cluster}.{schema}/{tbl}/_description'
    TABLE_DESCRIPTION_RELATION_TYPE = 'DESCRIPTION'
    DESCRIPTION_TABLE_RELATION_TYPE = 'DESCRIPTION_OF'

    DATABASE_NODE_LABEL = 'Database'
    DATABASE_KEY_FORMAT = 'database://{db}'
    DATABASE_CLUSTER_RELATION_TYPE = 'CLUSTER'
    CLUSTER_DATABASE_RELATION_TYPE = 'CLUSTER_OF'

    CLUSTER_NODE_LABEL = 'Cluster'
    CLUSTER_KEY_FORMAT = '{db}://{cluster}'
    CLUSTER_SCHEMA_RELATION_TYPE = 'SCHEMA'
    SCHEMA_CLUSTER_RELATION_TYPE = 'SCHEMA_OF'

    SCHEMA_NODE_LABEL = 'Schema'
    SCHEMA_KEY_FORMAT = '{db}://{cluster}.{schema}'
    SCHEMA_TABLE_RELATION_TYPE = 'TABLE'
    TABLE_SCHEMA_RELATION_TYPE = 'TABLE_OF'

    TABLE_COL_RELATION_TYPE = 'COLUMN'
    COL_TABLE_RELATION_TYPE = 'COLUMN_OF'

    # Only for deduping database, cluster, and schema (table and column will be always processed)
    serialized_nodes = set()  # type: Set[Any]
    serialized_rels = set()  # type: Set[Any]

    def __init__(self,
                 database,  # type: str
                 cluster,  # type: str
                 schema_name,  # type: str
                 name,  # type: str
                 description,  # type: Union[str, None]
                 columns=None,  # type: Iterable[ColumnMetadata]
                 is_view=False,  # type: bool
                 ):
        # type: (...) -> None
        """
        TODO: Add owners
        :param database:
        :param cluster:
        :param schema_name:
        :param name:
        :param description:
        :param columns:
        """
        self.database = database
        self.cluster = cluster
        self.schema_name = schema_name
        self.name = name
        self.description = description
        self.columns = columns if columns else []
        self.is_view = is_view
        self._node_iterator = self._create_next_node()
        self._relation_iterator = self._create_next_relation()

    def __repr__(self):
        # type: () -> str
        return 'TableMetadata({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r})'.format(self.database,
                                                                                self.cluster,
                                                                                self.schema_name,
                                                                                self.name,
                                                                                self.description,
                                                                                self.columns,
                                                                                self.is_view)

    def _get_table_key(self):
        # type: () -> str
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.database,
                                                     cluster=self.cluster,
                                                     schema=self.schema_name,
                                                     tbl=self.name)

    def _get_table_description_key(self):
        # type: () -> str
        return TableMetadata.TABLE_DESCRIPTION_FORMAT.format(db=self.database,
                                                             cluster=self.cluster,
                                                             schema=self.schema_name,
                                                             tbl=self.name)

    def _get_database_key(self):
        # type: () -> str
        return TableMetadata.DATABASE_KEY_FORMAT.format(db=self.database)

    def _get_cluster_key(self):
        # type: () -> str
        return TableMetadata.CLUSTER_KEY_FORMAT.format(db=self.database,
                                                       cluster=self.cluster)

    def _get_schema_key(self):
        # type: () -> str
        return TableMetadata.SCHEMA_KEY_FORMAT.format(db=self.database,
                                                      cluster=self.cluster,
                                                      schema=self.schema_name)

    def _get_col_key(self, col):
        # type: (ColumnMetadata) -> str
        return ColumnMetadata.COLUMN_KEY_FORMAT.format(db=self.database,
                                                       cluster=self.cluster,
                                                       schema=self.schema_name,
                                                       tbl=self.name,
                                                       col=col.name)

    def _get_col_description_key(self, col):
        # type: (ColumnMetadata) -> str
        return ColumnMetadata.COLUMN_DESCRIPTION_FORMAT.format(db=self.database,
                                                               cluster=self.cluster,
                                                               schema=self.schema_name,
                                                               tbl=self.name,
                                                               col=col.name)

    def create_next_node(self):
        # type: () -> Union[Dict[str, Any], None]
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_next_node(self):
        # type: () -> Iterator[Any]
        yield {NODE_LABEL: TableMetadata.TABLE_NODE_LABEL,
               NODE_KEY: self._get_table_key(),
               TableMetadata.TABLE_NAME: self.name,
               TableMetadata.IS_VIEW: self.is_view}

        if self.description:
            yield {NODE_LABEL: DESCRIPTION_NODE_LABEL,
                   NODE_KEY: self._get_table_description_key(),
                   TableMetadata.TABLE_DESCRIPTION: self.description}

        for col in self.columns:
            yield {
                NODE_LABEL: ColumnMetadata.COLUMN_NODE_LABEL,
                NODE_KEY: self._get_col_key(col),
                ColumnMetadata.COLUMN_NAME: col.name,
                ColumnMetadata.COLUMN_TYPE: col.type,
                ColumnMetadata.COLUMN_ORDER: col.sort_order}

            if not col.description:
                continue

            yield {
                NODE_LABEL: DESCRIPTION_NODE_LABEL,
                NODE_KEY: self._get_col_description_key(col),
                ColumnMetadata.COLUMN_DESCRIPTION: col.description}

        # Database, cluster, schema
        others = [NodeTuple(key=self._get_database_key(),
                            name=self.database,
                            label=TableMetadata.DATABASE_NODE_LABEL),
                  NodeTuple(key=self._get_cluster_key(),
                            name=self.cluster,
                            label=TableMetadata.CLUSTER_NODE_LABEL),
                  NodeTuple(key=self._get_schema_key(),
                            name=self.schema_name,
                            label=TableMetadata.SCHEMA_NODE_LABEL)
                  ]

        for node_tuple in others:
            if node_tuple not in TableMetadata.serialized_nodes:
                TableMetadata.serialized_nodes.add(node_tuple)
                yield {
                    NODE_LABEL: node_tuple.label,
                    NODE_KEY: node_tuple.key,
                    'name': node_tuple.name
                }

    def create_next_relation(self):
        # type: () -> Union[Dict[str, Any], None]
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_next_relation(self):
        # type: () -> Iterator[Any]

        yield {
            RELATION_START_LABEL: TableMetadata.SCHEMA_NODE_LABEL,
            RELATION_END_LABEL: TableMetadata.TABLE_NODE_LABEL,
            RELATION_START_KEY: self._get_schema_key(),
            RELATION_END_KEY: self._get_table_key(),
            RELATION_TYPE: TableMetadata.SCHEMA_TABLE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableMetadata.TABLE_SCHEMA_RELATION_TYPE
        }

        if self.description:
            yield {
                RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
                RELATION_END_LABEL: DESCRIPTION_NODE_LABEL,
                RELATION_START_KEY: self._get_table_key(),
                RELATION_END_KEY: self._get_table_description_key(),
                RELATION_TYPE: TableMetadata.TABLE_DESCRIPTION_RELATION_TYPE,
                RELATION_REVERSE_TYPE: TableMetadata.DESCRIPTION_TABLE_RELATION_TYPE
            }

        for col in self.columns:
            yield {
                RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
                RELATION_END_LABEL: ColumnMetadata.COLUMN_NODE_LABEL,
                RELATION_START_KEY: self._get_table_key(),
                RELATION_END_KEY: self._get_col_key(col),
                RELATION_TYPE: TableMetadata.TABLE_COL_RELATION_TYPE,
                RELATION_REVERSE_TYPE: TableMetadata.COL_TABLE_RELATION_TYPE
            }

            if not col.description:
                continue

            yield {
                RELATION_START_LABEL: ColumnMetadata.COLUMN_NODE_LABEL,
                RELATION_END_LABEL: DESCRIPTION_NODE_LABEL,
                RELATION_START_KEY: self._get_col_key(col),
                RELATION_END_KEY: self._get_col_description_key(col),
                RELATION_TYPE: ColumnMetadata.COL_DESCRIPTION_RELATION_TYPE,
                RELATION_REVERSE_TYPE: ColumnMetadata.DESCRIPTION_COL_RELATION_TYPE
            }

        others = [
            RelTuple(start_label=TableMetadata.DATABASE_NODE_LABEL,
                     end_label=TableMetadata.CLUSTER_NODE_LABEL,
                     start_key=self._get_database_key(),
                     end_key=self._get_cluster_key(),
                     type=TableMetadata.DATABASE_CLUSTER_RELATION_TYPE,
                     reverse_type=TableMetadata.CLUSTER_DATABASE_RELATION_TYPE),
            RelTuple(start_label=TableMetadata.CLUSTER_NODE_LABEL,
                     end_label=TableMetadata.SCHEMA_NODE_LABEL,
                     start_key=self._get_cluster_key(),
                     end_key=self._get_schema_key(),
                     type=TableMetadata.CLUSTER_SCHEMA_RELATION_TYPE,
                     reverse_type=TableMetadata.SCHEMA_CLUSTER_RELATION_TYPE)
        ]

        for rel_tuple in others:
            if rel_tuple not in TableMetadata.serialized_rels:
                TableMetadata.serialized_rels.add(rel_tuple)
                yield {
                    RELATION_START_LABEL: rel_tuple.start_label,
                    RELATION_END_LABEL: rel_tuple.end_label,
                    RELATION_START_KEY: rel_tuple.start_key,
                    RELATION_END_KEY: rel_tuple.end_key,
                    RELATION_TYPE: rel_tuple.type,
                    RELATION_REVERSE_TYPE: rel_tuple.reverse_type
                }
