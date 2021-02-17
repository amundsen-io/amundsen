# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import ANY

from databuilder.models.application import Application
from databuilder.models.graph_serializable import (
    NODE_KEY, NODE_LABEL, RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY,
    RELATION_START_LABEL, RELATION_TYPE,
)
from databuilder.models.table_metadata import TableMetadata
from databuilder.serializers import neo4_serializer, neptune_serializer
from databuilder.serializers.neptune_serializer import (
    NEPTUNE_CREATION_TYPE_JOB, NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT,
    NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_HEADER_ID, NEPTUNE_HEADER_LABEL,
    NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_RELATIONSHIP_HEADER_FROM,
    NEPTUNE_RELATIONSHIP_HEADER_TO,
)


class TestApplication(unittest.TestCase):

    def setUp(self) -> None:
        super(TestApplication, self).setUp()

        self.application = Application(task_id='hive.default.test_table',
                                       dag_id='event_test',
                                       schema='default',
                                       table_name='test_table',
                                       application_url_template='airflow_host.net/admin/airflow/tree?dag_id={dag_id}')

        self.expected_node_result = {
            NODE_KEY: 'application://gold.airflow/event_test/hive.default.test_table',
            NODE_LABEL: 'Application',
            'application_url': 'airflow_host.net/admin/airflow/tree?dag_id=event_test',
            'id': 'event_test/hive.default.test_table',
            'name': 'Airflow',
            'description': 'Airflow with id event_test/hive.default.test_table'
        }

        self.expected_relation_result = {
            RELATION_START_KEY: 'hive://gold.default/test_table',
            RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
            RELATION_END_KEY: 'application://gold.airflow/event_test/hive.default.test_table',
            RELATION_END_LABEL: 'Application',
            RELATION_TYPE: 'DERIVED_FROM',
            RELATION_REVERSE_TYPE: 'GENERATES'
        }

    def test_create_next_node(self) -> None:
        next_node = self.application.create_next_node()
        serialized_next_node = neo4_serializer.serialize_node(next_node)
        self.assertEquals(serialized_next_node, self.expected_node_result)

    def test_create_next_node_neptune(self) -> None:
        next_node = self.application.create_next_node()
        serialized_next_node = neptune_serializer.convert_node(next_node)
        neptune_expected = {
            NEPTUNE_HEADER_ID: 'application://gold.airflow/event_test/hive.default.test_table',
            NEPTUNE_HEADER_LABEL: 'Application',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            'application_url:String(single)': 'airflow_host.net/admin/airflow/tree?dag_id=event_test',
            'id:String(single)': 'event_test/hive.default.test_table',
            'name:String(single)': 'Airflow',
            'description:String(single)': 'Airflow with id event_test/hive.default.test_table',
        }
        self.assertDictEqual(neptune_expected, serialized_next_node)

    def test_create_next_relation(self) -> None:
        next_relation = self.application.create_next_relation()
        serialized_next_relation = neo4_serializer.serialize_relationship(next_relation)
        self.assertEquals(serialized_next_relation, self.expected_relation_result)

    def test_create_next_relation_neptune(self) -> None:

        neptune_forward_expected = {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.default/test_table',
                to_vertex_id='application://gold.airflow/event_test/hive.default.test_table',
                label='DERIVED_FROM'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.default/test_table',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'application://gold.airflow/event_test/hive.default.test_table',
            NEPTUNE_HEADER_LABEL: 'DERIVED_FROM',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }

        neptune_reversed_expected = {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='application://gold.airflow/event_test/hive.default.test_table',
                to_vertex_id='hive://gold.default/test_table',
                label='GENERATES'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'application://gold.airflow/event_test/hive.default.test_table',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.default/test_table',
            NEPTUNE_HEADER_LABEL: 'GENERATES',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }

        next_relation = self.application.create_next_relation()
        serialized_next_relations = neptune_serializer.convert_relationship(next_relation)
        self.assertDictEqual(serialized_next_relations[0], neptune_forward_expected)
        self.assertDictEqual(serialized_next_relations[1], neptune_reversed_expected)

    def test_get_table_model_key(self) -> None:
        table = self.application.get_table_model_key()
        self.assertEqual(table, 'hive://gold.default/test_table')

    def test_get_application_model_key(self) -> None:
        application = self.application.get_application_model_key()
        self.assertEqual(application, self.expected_node_result[NODE_KEY])

    def test_create_nodes(self) -> None:
        nodes = self.application.create_nodes()
        self.assertEquals(len(nodes), 1)
        serialized_next_node = neo4_serializer.serialize_node(nodes[0])
        self.assertEquals(serialized_next_node, self.expected_node_result)

    def test_create_relation(self) -> None:
        relation = self.application.create_relation()
        self.assertEquals(len(relation), 1)
        self.assertEquals(neo4_serializer.serialize_relationship(relation[0]), self.expected_relation_result)
