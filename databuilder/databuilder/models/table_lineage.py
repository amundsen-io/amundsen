# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import re
from typing import Any, Dict, List, Union

from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable, \
    RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE

from databuilder.models.table_metadata import TableMetadata


class TableLineage(Neo4jCsvSerializable):
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
                 downstream_deps: List=None,
                 ) -> None:
        self.db = db_name.lower()
        self.schema = schema.lower()
        self.table = table_name.lower()

        self.cluster = cluster.lower() if cluster else 'gold'
        # a list of downstream dependencies, each of which will follow
        # the same key
        self.downstream_deps = downstream_deps or []
        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def create_next_node(self) -> Union[Dict[str, Any], None]:
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Union[Dict[str, Any], None]:
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
        return '{db}://{cluster}.{schema}/{table}'.format(db=db,
                                                          cluster=cluster,
                                                          schema=schema,
                                                          table=table)

    def create_nodes(self) -> List[Union[Dict[str, Any], None]]:
        """
        It won't create any node for this model
        :return:
        """
        return []

    def create_relation(self) -> List[Dict[str, Any]]:
        """
        Create a list of relation between source table and all the downstream tables
        :return:
        """
        results = []
        for downstream_tab in self.downstream_deps:
            # every deps should follow '{db}://{cluster}.{schema}/{table}'
            # todo: if we change the table uri, we should change here.
            m = re.match('(\w+)://(\w+)\.(\w+)\/(\w+)', downstream_tab)
            if m:
                # if not match, skip those records
                results.append({
                    RELATION_START_KEY: self.get_table_model_key(db=self.db,
                                                                 cluster=self.cluster,
                                                                 schema=self.schema,
                                                                 table=self.table),
                    RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
                    RELATION_END_KEY: self.get_table_model_key(db=m.group(1),
                                                               cluster=m.group(2),
                                                               schema=m.group(3),
                                                               table=m.group(4)),
                    RELATION_END_LABEL: TableMetadata.TABLE_NODE_LABEL,
                    RELATION_TYPE: TableLineage.ORIGIN_DEPENDENCY_RELATION_TYPE,
                    RELATION_REVERSE_TYPE: TableLineage.DEPENDENCY_ORIGIN_RELATION_TYPE
                })
        return results

    def __repr__(self) -> str:
        return 'TableLineage({!r}, {!r}, {!r}, {!r})'.format(self.db,
                                                             self.cluster,
                                                             self.schema,
                                                             self.table)
