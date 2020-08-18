# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from databuilder.models.application import Application

from databuilder.models.neo4j_csv_serde import NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE

from databuilder.models.table_metadata import TableMetadata


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
        self.assertEquals(next_node, self.expected_node_result)

    def test_create_next_relation(self) -> None:
        next_relation = self.application.create_next_relation()
        self.assertEquals(next_relation, self.expected_relation_result)

    def test_get_table_model_key(self) -> None:
        table = self.application.get_table_model_key()
        self.assertEquals(table, 'hive://gold.default/test_table')

    def test_get_application_model_key(self) -> None:
        application = self.application.get_application_model_key()
        self.assertEquals(application, self.expected_node_result[NODE_KEY])

    def test_create_nodes(self) -> None:
        nodes = self.application.create_nodes()
        self.assertEquals(len(nodes), 1)
        self.assertEquals(nodes[0], self.expected_node_result)

    def test_create_relation(self) -> None:
        relation = self.application.create_relation()
        self.assertEquals(len(relation), 1)
        self.assertEquals(relation[0], self.expected_relation_result)
