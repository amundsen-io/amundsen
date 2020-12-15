# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import copy
from typing import (
    Any, Dict, Iterable, Iterator, List, Optional, Set, Union,
)

from databuilder.models.badge import Badge, BadgeMetadata
from databuilder.models.cluster import cluster_constants
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.schema import schema_constant

DESCRIPTION_NODE_LABEL_VAL = 'Description'
DESCRIPTION_NODE_LABEL = DESCRIPTION_NODE_LABEL_VAL


def _format_as_list(tags: Union[List, str, None]) -> List:
    if tags is None:
        tags = []
    if isinstance(tags, str):
        tags = list(filter(None, tags.split(',')))
    if isinstance(tags, list):
        tags = [tag.lower().strip() for tag in tags]
    return tags


class TagMetadata(GraphSerializable):
    TAG_NODE_LABEL = 'Tag'
    TAG_KEY_FORMAT = '{tag}'
    TAG_TYPE = 'tag_type'
    DEFAULT_TYPE = 'default'
    BADGE_TYPE = 'badge'
    DASHBOARD_TYPE = 'dashboard'
    METRIC_TYPE = 'metric'

    def __init__(self,
                 name: str,
                 tag_type: str = 'default',
                 ):
        self._name = name
        self._tag_type = tag_type
        self._nodes = iter([self.create_tag_node(self._name, self._tag_type)])
        self._relations: Iterator[GraphRelationship] = iter([])

    @staticmethod
    def get_tag_key(name: str) -> str:
        if not name:
            return ''
        return TagMetadata.TAG_KEY_FORMAT.format(tag=name)

    @staticmethod
    def create_tag_node(name: str, tag_type: str = DEFAULT_TYPE) -> GraphNode:
        node = GraphNode(
            key=TagMetadata.get_tag_key(name),
            label=TagMetadata.TAG_NODE_LABEL,
            attributes={
                TagMetadata.TAG_TYPE: tag_type
            }
        )
        return node

    def create_next_node(self) -> Optional[GraphNode]:
        # return the string representation of the data
        try:
            return next(self._nodes)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        # We don't emit any relations for Tag ingestion
        try:
            return next(self._relations)
        except StopIteration:
            return None


# TODO: this should inherit from ProgrammaticDescription in amundsen-common
class DescriptionMetadata:
    DESCRIPTION_NODE_LABEL = DESCRIPTION_NODE_LABEL_VAL
    PROGRAMMATIC_DESCRIPTION_NODE_LABEL = 'Programmatic_Description'
    DESCRIPTION_KEY_FORMAT = '{description}'
    DESCRIPTION_TEXT = 'description'
    DESCRIPTION_SOURCE = 'description_source'

    DESCRIPTION_RELATION_TYPE = 'DESCRIPTION'
    INVERSE_DESCRIPTION_RELATION_TYPE = 'DESCRIPTION_OF'

    # The default editable source.
    DEFAULT_SOURCE = "description"

    def __init__(self,
                 text: Optional[str],
                 source: str = DEFAULT_SOURCE
                 ):
        """
        :param source: The unique source of what is populating this description.
        :param text: the description text. Markdown supported.
        """
        self._source = source
        self._text = text
        #  There are so many dependencies on Description node, that it is probably easier to just separate the rest out.
        if (self._source == self.DEFAULT_SOURCE):
            self._label = self.DESCRIPTION_NODE_LABEL
        else:
            self._label = self.PROGRAMMATIC_DESCRIPTION_NODE_LABEL

    @staticmethod
    def create_description_metadata(text: Union[None, str],
                                    source: Optional[str] = DEFAULT_SOURCE
                                    ) -> Optional['DescriptionMetadata']:
        # We do not want to create a node if there is no description text!
        if text is None:
            return None
        if not source:
            description_node = DescriptionMetadata(text=text, source=DescriptionMetadata.DEFAULT_SOURCE)
        else:
            description_node = DescriptionMetadata(text=text, source=source)
        return description_node

    def get_description_id(self) -> str:
        if self._source == self.DEFAULT_SOURCE:
            return "_description"
        else:
            return "_" + self._source + "_description"

    def __repr__(self) -> str:
        return f'DescriptionMetadata({self._source!r}, {self._text!r})'

    def get_node(self, node_key: str) -> GraphNode:
        node = GraphNode(
            key=node_key,
            label=self._label,
            attributes={
                DescriptionMetadata.DESCRIPTION_SOURCE: self._source,
                DescriptionMetadata.DESCRIPTION_TEXT: self._text
            }
        )
        return node

    def get_relation(self, start_node: str, start_key: Any, end_key: Any) -> GraphRelationship:
        relationship = GraphRelationship(
            start_label=start_node,
            start_key=start_key,
            end_label=self._label,
            end_key=end_key,
            type=DescriptionMetadata.DESCRIPTION_RELATION_TYPE,
            reverse_type=DescriptionMetadata.INVERSE_DESCRIPTION_RELATION_TYPE,
            attributes={}
        )
        return relationship


class ColumnMetadata:
    COLUMN_NODE_LABEL = 'Column'
    COLUMN_KEY_FORMAT = '{db}://{cluster}.{schema}/{tbl}/{col}'
    COLUMN_NAME = 'name'
    COLUMN_TYPE = 'type'
    COLUMN_ORDER = 'sort_order'
    COLUMN_DESCRIPTION = 'description'
    COLUMN_DESCRIPTION_FORMAT = '{db}://{cluster}.{schema}/{tbl}/{col}/{description_id}'

    def __init__(self,
                 name: str,
                 description: Union[str, None],
                 col_type: str,
                 sort_order: int,
                 badges: Union[List[str], None] = None,
                 ) -> None:
        """
        TODO: Add stats
        :param name:
        :param description:
        :param col_type:
        :param sort_order:
        :param badges: Optional. Column level badges
        """
        self.name = name
        self.description = DescriptionMetadata.create_description_metadata(source=None,
                                                                           text=description)
        self.type = col_type
        self.sort_order = sort_order
        formatted_badges = _format_as_list(badges)
        self.badges = [Badge(badge, 'column') for badge in formatted_badges]

    def __repr__(self) -> str:
        return f'ColumnMetadata({self.name!r}, {self.description!r}, {self.type!r}, ' \
               f'{self.sort_order!r}, {self.badges!r})'


class TableMetadata(GraphSerializable):
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
    IS_VIEW = 'is_view'

    TABLE_DESCRIPTION_FORMAT = '{db}://{cluster}.{schema}/{tbl}/{description_id}'

    DATABASE_NODE_LABEL = 'Database'
    DATABASE_KEY_FORMAT = 'database://{db}'
    DATABASE_CLUSTER_RELATION_TYPE = cluster_constants.CLUSTER_RELATION_TYPE
    CLUSTER_DATABASE_RELATION_TYPE = cluster_constants.CLUSTER_REVERSE_RELATION_TYPE

    CLUSTER_NODE_LABEL = cluster_constants.CLUSTER_NODE_LABEL
    CLUSTER_KEY_FORMAT = '{db}://{cluster}'
    CLUSTER_SCHEMA_RELATION_TYPE = schema_constant.SCHEMA_RELATION_TYPE
    SCHEMA_CLUSTER_RELATION_TYPE = schema_constant.SCHEMA_REVERSE_RELATION_TYPE

    SCHEMA_NODE_LABEL = schema_constant.SCHEMA_NODE_LABEL
    SCHEMA_KEY_FORMAT = schema_constant.DATABASE_SCHEMA_KEY_FORMAT
    SCHEMA_TABLE_RELATION_TYPE = 'TABLE'
    TABLE_SCHEMA_RELATION_TYPE = 'TABLE_OF'

    TABLE_COL_RELATION_TYPE = 'COLUMN'
    COL_TABLE_RELATION_TYPE = 'COLUMN_OF'

    TABLE_TAG_RELATION_TYPE = 'TAGGED_BY'
    TAG_TABLE_RELATION_TYPE = 'TAG'

    # Only for deduping database, cluster, and schema (table and column will be always processed)
    serialized_nodes_keys: Set[Any] = set()
    serialized_rels_keys: Set[Any] = set()

    def __init__(self,
                 database: str,
                 cluster: str,
                 schema: str,
                 name: str,
                 description: Union[str, None],
                 columns: Iterable[ColumnMetadata] = None,
                 is_view: bool = False,
                 tags: Union[List, str] = None,
                 description_source: Union[str, None] = None,
                 **kwargs: Any
                 ) -> None:
        """
        :param database:
        :param cluster:
        :param schema:
        :param name:
        :param description:
        :param columns:
        :param is_view: Indicate whether the table is a view or not
        :param tags:
        :param description_source: Optional. Where the description is coming from. Used to compose unique id.
        :param kwargs: Put additional attributes to the table model if there is any.
        """
        self.database = database
        self.cluster = cluster
        self.schema = schema
        self.name = name
        self.description = DescriptionMetadata.create_description_metadata(text=description, source=description_source)
        self.columns = columns if columns else []
        self.is_view = is_view
        self.attrs: Optional[Dict[str, Any]] = None

        self.tags = _format_as_list(tags)

        if kwargs:
            self.attrs = copy.deepcopy(kwargs)

        self._node_iterator = self._create_next_node()
        self._relation_iterator = self._create_next_relation()

    def __repr__(self) -> str:
        return f'TableMetadata({self.database!r}, {self.cluster!r}, {self.schema!r}, {self.name!r} ' \
               f'{self.description!r}, {self.columns!r}, {self.is_view!r}, {self.tags!r})'

    def _get_table_key(self) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.database,
                                                     cluster=self.cluster,
                                                     schema=self.schema,
                                                     tbl=self.name)

    def _get_table_description_key(self, description: DescriptionMetadata) -> str:
        return TableMetadata.TABLE_DESCRIPTION_FORMAT.format(db=self.database,
                                                             cluster=self.cluster,
                                                             schema=self.schema,
                                                             tbl=self.name,
                                                             description_id=description.get_description_id())

    def _get_database_key(self) -> str:
        return TableMetadata.DATABASE_KEY_FORMAT.format(db=self.database)

    def _get_cluster_key(self) -> str:
        return TableMetadata.CLUSTER_KEY_FORMAT.format(db=self.database,
                                                       cluster=self.cluster)

    def _get_schema_key(self) -> str:
        return TableMetadata.SCHEMA_KEY_FORMAT.format(db=self.database,
                                                      cluster=self.cluster,
                                                      schema=self.schema)

    def _get_col_key(self, col: ColumnMetadata) -> str:
        return ColumnMetadata.COLUMN_KEY_FORMAT.format(db=self.database,
                                                       cluster=self.cluster,
                                                       schema=self.schema,
                                                       tbl=self.name,
                                                       col=col.name,
                                                       badges=col.badges)

    def _get_col_description_key(self,
                                 col: ColumnMetadata,
                                 description: DescriptionMetadata) -> str:
        return ColumnMetadata.COLUMN_DESCRIPTION_FORMAT.format(db=self.database,
                                                               cluster=self.cluster,
                                                               schema=self.schema,
                                                               tbl=self.name,
                                                               col=col.name,
                                                               description_id=description.get_description_id())

    @staticmethod
    def format_tags(tags: Union[List, str, None]) -> List:
        return _format_as_list(tags)

    def create_next_node(self) -> Union[GraphNode, None]:
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_next_node(self) -> Iterator[GraphNode]:
        yield self._create_table_node()

        if self.description:
            node_key = self._get_table_description_key(self.description)
            yield self.description.get_node(node_key)

        # Create the table tag nodes
        if self.tags:
            for tag in self.tags:
                yield TagMetadata.create_tag_node(tag)

        for col in self.columns:
            column_node = GraphNode(
                key=self._get_col_key(col),
                label=ColumnMetadata.COLUMN_NODE_LABEL,
                attributes={
                    ColumnMetadata.COLUMN_NAME: col.name,
                    ColumnMetadata.COLUMN_TYPE: col.type,
                    ColumnMetadata.COLUMN_ORDER: col.sort_order
                }
            )
            yield column_node

            if col.description:
                node_key = self._get_col_description_key(col, col.description)
                yield col.description.get_node(node_key)

            if col.badges:
                col_badge_metadata = BadgeMetadata(
                    start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                    start_key=self._get_col_key(col),
                    badges=col.badges)
                for node in col_badge_metadata.create_nodes():
                    yield node

        # Database, cluster, schema
        others = [
            GraphNode(
                key=self._get_database_key(),
                label=TableMetadata.DATABASE_NODE_LABEL,
                attributes={
                    'name': self.database
                }
            ),
            GraphNode(
                key=self._get_cluster_key(),
                label=TableMetadata.CLUSTER_NODE_LABEL,
                attributes={
                    'name': self.cluster
                }
            ),
            GraphNode(
                key=self._get_schema_key(),
                label=TableMetadata.SCHEMA_NODE_LABEL,
                attributes={
                    'name': self.schema
                }
            )
        ]

        for node_tuple in others:
            if node_tuple.key not in TableMetadata.serialized_nodes_keys:
                TableMetadata.serialized_nodes_keys.add(node_tuple.key)
                yield node_tuple

    def _create_table_node(self) -> GraphNode:
        table_attributes = {
            TableMetadata.TABLE_NAME: self.name,
            TableMetadata.IS_VIEW: self.is_view
        }
        if self.attrs:
            for k, v in self.attrs.items():
                if k not in table_attributes:
                    table_attributes[k] = v

        return GraphNode(
            key=self._get_table_key(),
            label=TableMetadata.TABLE_NODE_LABEL,
            attributes=table_attributes
        )

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_next_relation(self) -> Iterator[GraphRelationship]:
        schema_table_relationship = GraphRelationship(
            start_key=self._get_schema_key(),
            start_label=TableMetadata.SCHEMA_NODE_LABEL,
            end_key=self._get_table_key(),
            end_label=TableMetadata.TABLE_NODE_LABEL,
            type=TableMetadata.SCHEMA_TABLE_RELATION_TYPE,
            reverse_type=TableMetadata.TABLE_SCHEMA_RELATION_TYPE,
            attributes={}
        )
        yield schema_table_relationship

        if self.description:
            yield self.description.get_relation(TableMetadata.TABLE_NODE_LABEL,
                                                self._get_table_key(),
                                                self._get_table_description_key(self.description))

        if self.tags:
            for tag in self.tags:
                tag_relationship = GraphRelationship(
                    start_label=TableMetadata.TABLE_NODE_LABEL,
                    start_key=self._get_table_key(),
                    end_label=TagMetadata.TAG_NODE_LABEL,
                    end_key=TagMetadata.get_tag_key(tag),
                    type=TableMetadata.TABLE_TAG_RELATION_TYPE,
                    reverse_type=TableMetadata.TAG_TABLE_RELATION_TYPE,
                    attributes={}
                )
                yield tag_relationship

        for col in self.columns:
            column_relationship = GraphRelationship(
                start_label=TableMetadata.TABLE_NODE_LABEL,
                start_key=self._get_table_key(),
                end_label=ColumnMetadata.COLUMN_NODE_LABEL,
                end_key=self._get_col_key(col),
                type=TableMetadata.TABLE_COL_RELATION_TYPE,
                reverse_type=TableMetadata.COL_TABLE_RELATION_TYPE,
                attributes={}
            )
            yield column_relationship

            if col.description:
                yield col.description.get_relation(
                    ColumnMetadata.COLUMN_NODE_LABEL,
                    self._get_col_key(col),
                    self._get_col_description_key(col, col.description)
                )

            if col.badges:
                badge_metadata = BadgeMetadata(start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                               start_key=self._get_col_key(col),
                                               badges=col.badges)
                badge_relations = badge_metadata.create_relation()
                for relation in badge_relations:
                    yield relation

        others = [
            GraphRelationship(
                start_label=TableMetadata.DATABASE_NODE_LABEL,
                end_label=TableMetadata.CLUSTER_NODE_LABEL,
                start_key=self._get_database_key(),
                end_key=self._get_cluster_key(),
                type=TableMetadata.DATABASE_CLUSTER_RELATION_TYPE,
                reverse_type=TableMetadata.CLUSTER_DATABASE_RELATION_TYPE,
                attributes={}
            ),
            GraphRelationship(
                start_label=TableMetadata.CLUSTER_NODE_LABEL,
                end_label=TableMetadata.SCHEMA_NODE_LABEL,
                start_key=self._get_cluster_key(),
                end_key=self._get_schema_key(),
                type=TableMetadata.CLUSTER_SCHEMA_RELATION_TYPE,
                reverse_type=TableMetadata.SCHEMA_CLUSTER_RELATION_TYPE,
                attributes={}
            )
        ]

        for rel_tuple in others:
            if (rel_tuple.start_key, rel_tuple.end_key, rel_tuple.type) not in TableMetadata.serialized_rels_keys:
                TableMetadata.serialized_rels_keys.add((rel_tuple.start_key, rel_tuple.end_key, rel_tuple.type))
                yield rel_tuple
