# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import ANY

from databuilder.models.graph_serializable import (
    RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY, RELATION_START_LABEL,
    RELATION_TYPE,
)
from databuilder.models.table_lineage import TableLineage
from databuilder.serializers import neo4_serializer, neptune_serializer
from databuilder.serializers.neptune_serializer import (
    NEPTUNE_CREATION_TYPE_JOB, NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_HEADER_ID,
    NEPTUNE_HEADER_LABEL, NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT,
    NEPTUNE_RELATIONSHIP_HEADER_FROM, NEPTUNE_RELATIONSHIP_HEADER_TO,
)

DB = 'hive'
SCHEMA = 'base'
TABLE = 'test'
CLUSTER = 'default'


class TestTableLineage(unittest.TestCase):

    def setUp(self) -> None:
        super(TestTableLineage, self).setUp()
        self.table_lineage = TableLineage(db_name='hive',
                                          schema=SCHEMA,
                                          table_name=TABLE,
                                          cluster=CLUSTER,
                                          downstream_deps=['hive://default.test_schema/test_table1',
                                                           'hive://default.test_schema/test_table2'])

        self.start_key = f'{DB}://{CLUSTER}.{SCHEMA}/{TABLE}'
        self.end_key = f'{DB}://{CLUSTER}.test_schema/test_table1'

    def test_get_table_model_key(self) -> None:
        metadata = self.table_lineage.get_table_model_key(db=DB,
                                                          cluster=CLUSTER,
                                                          schema=SCHEMA,
                                                          table=TABLE)
        self.assertEqual(metadata, 'hive://default.base/test')

    def test_create_nodes(self) -> None:
        nodes = self.table_lineage.create_nodes()
        self.assertEqual(len(nodes), 0)

    def test_create_relation(self) -> None:
        relations = self.table_lineage.create_relation()
        self.assertEqual(len(relations), 2)

        expected_relation = {
            RELATION_START_KEY: self.start_key,
            RELATION_START_LABEL: 'Table',
            RELATION_END_KEY: self.end_key,
            RELATION_END_LABEL: 'Table',
            RELATION_TYPE: TableLineage.ORIGIN_DEPENDENCY_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TableLineage.DEPENDENCY_ORIGIN_RELATION_TYPE
        }
        actual_relations = [
            neo4_serializer.serialize_relationship(relation)
            for relation in relations
        ]
        self.assertTrue(len(relations), 2)
        self.assertTrue(expected_relation in actual_relations)

    def test_create_relation_neptune(self) -> None:
        relations = self.table_lineage.create_relation()

        expected = [
            {
                NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                    from_vertex_id=self.start_key,
                    to_vertex_id=self.end_key,
                    label=TableLineage.ORIGIN_DEPENDENCY_RELATION_TYPE,
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: self.start_key,
                NEPTUNE_RELATIONSHIP_HEADER_TO: self.end_key,
                NEPTUNE_HEADER_LABEL: TableLineage.ORIGIN_DEPENDENCY_RELATION_TYPE,
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
            },
            {
                NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                    from_vertex_id=self.end_key,
                    to_vertex_id=self.start_key,
                    label=TableLineage.DEPENDENCY_ORIGIN_RELATION_TYPE
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: self.end_key,
                NEPTUNE_RELATIONSHIP_HEADER_TO: self.start_key,
                NEPTUNE_HEADER_LABEL: TableLineage.DEPENDENCY_ORIGIN_RELATION_TYPE,
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
            }
        ]
        actual_relations = [
            neptune_serializer.convert_relationship(relation)
            for relation in relations
        ]
        self.assertTrue(expected in actual_relations)
