# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from collections import namedtuple
from dataclasses import dataclass
from typing import Dict, List
from unittest.mock import ANY

from databuilder.models.application import Application, GenericApplication
from databuilder.models.graph_serializable import (
    NODE_KEY, NODE_LABEL, RELATION_END_KEY, RELATION_END_LABEL, RELATION_REVERSE_TYPE, RELATION_START_KEY,
    RELATION_START_LABEL, RELATION_TYPE,
)
from databuilder.models.table_metadata import TableMetadata
from databuilder.serializers import (
    mysql_serializer, neo4_serializer, neptune_serializer,
)
from databuilder.serializers.neptune_serializer import (
    METADATA_KEY_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_CREATION_TYPE_JOB,
    NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT,
    NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_HEADER_ID, NEPTUNE_HEADER_LABEL,
    NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_RELATIONSHIP_HEADER_FROM,
    NEPTUNE_RELATIONSHIP_HEADER_TO,
)


@dataclass
class ApplicationTestCase:
    application: GenericApplication
    expected_node_results: List[Dict]
    expected_relation_results: List[Dict]
    expected_records: List[Dict]


class TestApplication(unittest.TestCase):

    def setUp(self) -> None:
        super(TestApplication, self).setUp()

        self.test_cases = []

        # Explicitly add test case for Airflow to verify backwards compatibility
        airflow_application = Application(
            task_id='hive.default.test_table',
            dag_id='event_test',
            schema='default',
            table_name='test_table',
            application_url_template='airflow_host.net/admin/airflow/tree?dag_id={dag_id}',
        )

        airflow_expected_node_results = [{
            NODE_KEY: 'application://gold.airflow/event_test/hive.default.test_table',
            NODE_LABEL: 'Application',
            'application_url': 'airflow_host.net/admin/airflow/tree?dag_id=event_test',
            'id': 'event_test/hive.default.test_table',
            'name': 'Airflow',
            'description': 'Airflow with id event_test/hive.default.test_table'
        }]

        airflow_expected_relation_results = [{
            RELATION_START_KEY: 'hive://gold.default/test_table',
            RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
            RELATION_END_KEY: 'application://gold.airflow/event_test/hive.default.test_table',
            RELATION_END_LABEL: 'Application',
            RELATION_TYPE: 'DERIVED_FROM',
            RELATION_REVERSE_TYPE: 'GENERATES'
        }]

        airflow_expected_application_record = {
            'rk': 'application://gold.airflow/event_test/hive.default.test_table',
            'application_url': 'airflow_host.net/admin/airflow/tree?dag_id=event_test',
            'id': 'event_test/hive.default.test_table',
            'name': 'Airflow',
            'description': 'Airflow with id event_test/hive.default.test_table'
        }

        airflow_expected_application_table_record = {
            'rk': 'hive://gold.default/test_table',
            'application_rk': 'application://gold.airflow/event_test/hive.default.test_table'
        }

        airflow_expected_records = [
            airflow_expected_application_record,
            airflow_expected_application_table_record,
        ]

        self.test_cases.append(
            ApplicationTestCase(
                airflow_application,
                airflow_expected_node_results,
                airflow_expected_relation_results,
                airflow_expected_records,
            ),
        )

        # Test several non-airflow applications
        AppTestCase = namedtuple('AppTestCase', ['name', 'generates_table'])
        non_airflow_cases = [
            AppTestCase(name='Databricks', generates_table=False),
            AppTestCase(name='Snowflake', generates_table=True),
            AppTestCase(name='EMR', generates_table=False),
        ]

        for case in non_airflow_cases:
            application_type = case.name
            url = f'https://{application_type.lower()}.com/job/1234'
            id = f'{application_type}.hive.test_table'
            description = f'{application_type} application for hive.test_table'
            table_key = TableMetadata.TABLE_KEY_FORMAT.format(
                db='hive',
                cluster='gold',
                schema='default',
                tbl='test_table',
            )

            application = GenericApplication(
                start_label=TableMetadata.TABLE_NODE_LABEL,
                start_key=table_key,
                application_type=application_type,
                application_id=id,
                application_url=url,
                application_description=description,
                app_key_override=f'application://{application_type}/hive/test_table',
                generates_resource=case.generates_table,
            )

            expected_node_results = [{
                NODE_KEY: f'application://{application_type}/hive/test_table',
                NODE_LABEL: 'Application',
                'application_url': url,
                'id': id,
                'name': application_type,
                'description': description,
            }]

            expected_relation_results = [{
                RELATION_START_KEY: 'hive://gold.default/test_table',
                RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
                RELATION_END_KEY: f'application://{application_type}/hive/test_table',
                RELATION_END_LABEL: 'Application',
                RELATION_TYPE: (GenericApplication.DERIVED_FROM_REL_TYPE if case.generates_table
                                else GenericApplication.CONSUMED_BY_REL_TYPE),
                RELATION_REVERSE_TYPE: (GenericApplication.GENERATES_REL_TYPE if case.generates_table
                                        else GenericApplication.CONSUMES_REL_TYPE),
            }]

            expected_application_record = {
                'rk': f'application://{application_type}/hive/test_table',
                'application_url': url,
                'id': id,
                'name': application_type,
                'description': description,
            }

            expected_application_table_record = {
                'rk': 'hive://gold.default/test_table',
                'application_rk': f'application://{application_type}/hive/test_table'
            }

            expected_records = [
                expected_application_record,
                expected_application_table_record
            ]

            self.test_cases.append(
                ApplicationTestCase(
                    application,
                    expected_node_results,
                    expected_relation_results,
                    expected_records,
                ),
            )

    def test_get_application_model_key(self) -> None:
        for tc in self.test_cases:
            self.assertEqual(tc.application.application_key, tc.expected_node_results[0][NODE_KEY])

    def test_create_nodes(self) -> None:
        for tc in self.test_cases:
            actual = []
            node = tc.application.create_next_node()
            while node:
                serialized_next_node = neo4_serializer.serialize_node(node)
                actual.append(serialized_next_node)
                node = tc.application.create_next_node()

            self.assertEqual(actual, tc.expected_node_results)

    def test_create_nodes_neptune(self) -> None:
        for tc in self.test_cases:
            actual = []
            next_node = tc.application.create_next_node()
            while next_node:
                serialized_next_node = neptune_serializer.convert_node(next_node)
                actual.append(serialized_next_node)
                next_node = tc.application.create_next_node()

            node_id = f'Application:{tc.application.application_key}'
            node_key = tc.application.application_key
            neptune_expected = [{
                NEPTUNE_HEADER_ID: node_id,
                METADATA_KEY_PROPERTY_NAME_BULK_LOADER_FORMAT: node_key,
                NEPTUNE_HEADER_LABEL: 'Application',
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
                'application_url:String(single)': tc.application.application_url,
                'id:String(single)': tc.application.application_id,
                'name:String(single)': tc.application.application_type,
                'description:String(single)': tc.application.application_description,
            }]
            self.assertEqual(neptune_expected, actual)

    def test_create_relation(self) -> None:
        for tc in self.test_cases:
            actual = []
            relation = tc.application.create_next_relation()
            while relation:
                serialized_relation = neo4_serializer.serialize_relationship(relation)
                actual.append(serialized_relation)
                relation = tc.application.create_next_relation()

            self.assertEqual(actual, tc.expected_relation_results)

    def test_create_relations_neptune(self) -> None:
        for tc in self.test_cases:
            application_id = f'Application:{tc.application.application_key}'
            table_id = 'Table:hive://gold.default/test_table'
            neptune_forward_expected = {
                NEPTUNE_HEADER_ID: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                    from_vertex_id=table_id,
                    to_vertex_id=application_id,
                    label=tc.expected_relation_results[0][RELATION_TYPE],
                ),
                METADATA_KEY_PROPERTY_NAME_BULK_LOADER_FORMAT: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                    from_vertex_id=table_id,
                    to_vertex_id=application_id,
                    label=tc.expected_relation_results[0][RELATION_TYPE],
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: table_id,
                NEPTUNE_RELATIONSHIP_HEADER_TO: application_id,
                NEPTUNE_HEADER_LABEL: tc.expected_relation_results[0][RELATION_TYPE],
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
            }

            neptune_reversed_expected = {
                NEPTUNE_HEADER_ID: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                    from_vertex_id=application_id,
                    to_vertex_id=table_id,
                    label=tc.expected_relation_results[0][RELATION_REVERSE_TYPE],
                ),
                METADATA_KEY_PROPERTY_NAME_BULK_LOADER_FORMAT: "{label}:{from_vertex_id}_{to_vertex_id}".format(
                    from_vertex_id=application_id,
                    to_vertex_id=table_id,
                    label=tc.expected_relation_results[0][RELATION_REVERSE_TYPE],
                ),
                NEPTUNE_RELATIONSHIP_HEADER_FROM: application_id,
                NEPTUNE_RELATIONSHIP_HEADER_TO: table_id,
                NEPTUNE_HEADER_LABEL: tc.expected_relation_results[0][RELATION_REVERSE_TYPE],
                NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
                NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
            }
            neptune_expected = [[neptune_forward_expected, neptune_reversed_expected]]

            actual = []
            next_relation = tc.application.create_next_relation()
            while next_relation:
                serialized_next_relation = neptune_serializer.convert_relationship(next_relation)
                actual.append(serialized_next_relation)
                next_relation = tc.application.create_next_relation()

            self.assertEqual(actual, neptune_expected)

    def test_create_records(self) -> None:
        for tc in self.test_cases:
            expected = tc.expected_records

            actual = []
            record = tc.application.create_next_record()
            while record:
                serialized_record = mysql_serializer.serialize_record(record)
                actual.append(serialized_record)
                record = tc.application.create_next_record()

            self.assertEqual(expected, actual)
