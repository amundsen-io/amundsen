# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import re
from typing import (
    Iterator, List, Union,
)

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import TableMetadata


class TableLineage(GraphSerializable):
    """
    Table Lineage Model. It won't create nodes but create upstream/downstream rels.
    """
    LABEL = 'Lineage'
    KEY_FORMAT = '{db}://{cluster}.{schema}/{tbl}/'
    ORIGIN_DEPENDENCY_RELATION_TYPE = 'UPSTREAM'
    DEPENDENCY_ORIGIN_RELATION_TYPE = 'DOWNSTREAM'

    def __init__(self,
                 db_name: str,
                 schema: str,
                 table_name: str,
                 cluster: str,
                 downstream_deps: List = None,
                 ) -> None:
        self.db = db_name
        self.schema = schema
        self.table = table_name
        self.cluster = cluster if cluster else 'gold'
        # a list of downstream dependencies, each of which will follow
        # the same key
        self.downstream_deps = downstream_deps or []
        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_rel_iterator()

    def create_next_node(self) -> Union[GraphNode, None]:
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def get_table_model_key(self,
                            db: str,
                            cluster: str,
                            schema: str,
                            table: str
                            ) -> str:
        return f'{db}://{cluster}.{schema}/{table}'

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        """
        It won't create any node for this model
        :return:
        """
        return
        yield

    def _create_rel_iterator(self) -> Iterator[GraphRelationship]:
        """
        Create relations between source table and all the downstream tables
        :return:
        """
        for downstream_tab in self.downstream_deps:
            # every deps should follow '{db}://{cluster}.{schema}/{table}'
            # todo: if we change the table uri, we should change here.
            m = re.match('(\w+)://(\w+)\.(\w+)\/(\w+)', downstream_tab)
            if m:
                # if not match, skip those records
                relationship = GraphRelationship(
                    start_key=self.get_table_model_key(
                        db=self.db,
                        cluster=self.cluster,
                        schema=self.schema,
                        table=self.table
                    ),
                    start_label=TableMetadata.TABLE_NODE_LABEL,
                    end_label=TableMetadata.TABLE_NODE_LABEL,
                    end_key=self.get_table_model_key(
                        db=m.group(1),
                        cluster=m.group(2),
                        schema=m.group(3),
                        table=m.group(4)
                    ),
                    type=TableLineage.ORIGIN_DEPENDENCY_RELATION_TYPE,
                    reverse_type=TableLineage.DEPENDENCY_ORIGIN_RELATION_TYPE,
                    attributes={}
                )
                yield relationship

    def __repr__(self) -> str:
        return f'TableLineage({self.db!r}, {self.cluster!r}, {self.schema!r}, {self.table!r})'
