# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

# Validation of Cypher statements causing Flake8 to fail. Disabling it on this file only
# flake8: noqa

import logging
import textwrap
import unittest

from mock import patch
from neo4j import GraphDatabase
from pyhocon import ConfigFactory

from databuilder.publisher import neo4j_csv_publisher
from databuilder.task import neo4j_staleness_removal_task
from databuilder.task.neo4j_staleness_removal_task import Neo4jStalenessRemovalTask, TargetWithCondition


class TestRemoveStaleData(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)

    def test_validation_failure(self) -> None:

        with patch.object(GraphDatabase, 'driver'):
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 90,
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo'
            })

            task.init(job_config)
            total_record_count = 100
            stale_record_count = 50
            target_type = 'foo'
            task._validate_staleness_pct(total_record_count=total_record_count,
                                         stale_record_count=stale_record_count,
                                         target_type=target_type)

    def test_validation(self) -> None:

        with patch.object(GraphDatabase, 'driver'):
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo'
            })

            task.init(job_config)
            total_record_count = 100
            stale_record_count = 50
            target_type = 'foo'
            self.assertRaises(Exception, task._validate_staleness_pct, total_record_count, stale_record_count, target_type)

    def test_validation_threshold_override(self) -> None:

        with patch.object(GraphDatabase, 'driver'):
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_PCT_MAX_DICT}': {'foo': 51},
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo'
            })

            task.init(job_config)
            task._validate_staleness_pct(total_record_count=100,
                                         stale_record_count=50,
                                         target_type='foo')
            task._validate_staleness_pct(total_record_count=100,
                                         stale_record_count=3,
                                         target_type='bar')

    def test_marker(self) -> None:
        with patch.object(GraphDatabase, 'driver'):
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo'
            })

            task.init(job_config)
            self.assertIsNone(task.ms_to_expire)
            self.assertEqual(task.marker, 'foo')

            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.MS_TO_EXPIRE}': 86400000,
            })

            task.init(job_config)
            self.assertIsNotNone(task.ms_to_expire)
            self.assertEqual(task.marker, 86400000)

    def test_validation_statement_publish_tag(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo',
            })

            task.init(job_config)
            task._validate_node_staleness_pct()

            mock_execute.assert_called()
            mock_execute.assert_any_call(statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE true
            RETURN count(*) as count
            """))

            mock_execute.assert_any_call(param_dict={'marker': u'foo'},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.published_tag < $marker
            OR NOT EXISTS(target.published_tag))
            RETURN count(*) as count
            """))

            task._validate_relation_staleness_pct()
            mock_execute.assert_any_call(param_dict={'marker': u'foo'},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.published_tag < $marker
            OR NOT EXISTS(target.published_tag))
            RETURN count(*) as count
            """))

    def test_validation_statement_publish_tag_retain_data_with_no_publisher_metadata(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.RETAIN_DATA_WITH_NO_PUBLISHER_METADATA}': True
            })

            task.init(job_config)
            task._validate_node_staleness_pct()
            mock_execute.assert_any_call(param_dict={'marker': u'foo'},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.published_tag < $marker)
            RETURN count(*) as count
            """))

            task._validate_relation_staleness_pct()
            mock_execute.assert_any_call(param_dict={'marker': u'foo'},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.published_tag < $marker)
            RETURN count(*) as count
            """))

    def test_validation_statement_ms_to_expire(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.MS_TO_EXPIRE}': 9876543210
            })

            task.init(job_config)
            task._validate_node_staleness_pct()

            mock_execute.assert_called()
            mock_execute.assert_any_call(statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE true
            RETURN count(*) as count
            """))

            mock_execute.assert_any_call(param_dict={'marker': 9876543210},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.publisher_last_updated_epoch_ms < (timestamp() - $marker)
            OR NOT EXISTS(target.publisher_last_updated_epoch_ms))
            RETURN count(*) as count
            """))

            task._validate_relation_staleness_pct()
            mock_execute.assert_any_call(param_dict={'marker': 9876543210},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.publisher_last_updated_epoch_ms < (timestamp() - $marker)
            OR NOT EXISTS(target.publisher_last_updated_epoch_ms))
            RETURN count(*) as count
            """))

    def test_validation_statement_ms_to_expire_retain_data_with_no_publisher_metadata(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.MS_TO_EXPIRE}': 9876543210,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.RETAIN_DATA_WITH_NO_PUBLISHER_METADATA}': True
            })

            task.init(job_config)
            task._validate_node_staleness_pct()
            mock_execute.assert_any_call(param_dict={'marker': 9876543210},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.publisher_last_updated_epoch_ms < (timestamp() - $marker))
            RETURN count(*) as count
            """))

            task._validate_relation_staleness_pct()
            mock_execute.assert_any_call(param_dict={'marker': 9876543210},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.publisher_last_updated_epoch_ms < (timestamp() - $marker))
            RETURN count(*) as count
            """))

    def test_validation_statement_with_target_condition(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': [TargetWithCondition('Foo', '(target)-[:BAR]->(:Foo) AND target.name=\'foo_name\'')],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': [TargetWithCondition('BAR', '(start_node:Foo)-[target]->(end_node:Foo)')],
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo',
            })

            task.init(job_config)
            task._validate_node_staleness_pct()

            mock_execute.assert_called()
            mock_execute.assert_any_call(statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE true AND (target)-[:BAR]->(:Foo) AND target.name=\'foo_name\'
            RETURN count(*) as count
            """))

            mock_execute.assert_any_call(param_dict={'marker': u'foo'},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.published_tag < $marker
            OR NOT EXISTS(target.published_tag)) AND (target)-[:BAR]->(:Foo) AND target.name=\'foo_name\'
            RETURN count(*) as count
            """))

            task._validate_relation_staleness_pct()
            mock_execute.assert_any_call(param_dict={'marker': u'foo'},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.published_tag < $marker
            OR NOT EXISTS(target.published_tag)) AND (start_node:Foo)-[target]->(end_node:Foo)
            RETURN count(*) as count
            """))

    def test_validation_receives_correct_counts(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo',
            })

            task.init(job_config)

            with patch.object(Neo4jStalenessRemovalTask, '_validate_staleness_pct') as mock_validate:
                mock_execute.side_effect = [[{'count': 100}], [{'count': 50}]]
                task._validate_node_staleness_pct()
                mock_validate.assert_called_with(total_record_count=100,
                                                 stale_record_count=50,
                                                 target_type='Foo')

                mock_execute.side_effect = [[{'count': 100}], [{'count': 50}]]
                task._validate_relation_staleness_pct()
                mock_validate.assert_called_with(total_record_count=100,
                                                 stale_record_count=50,
                                                 target_type='BAR')

    def test_delete_statement_publish_tag(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            mock_execute.return_value.single.return_value = {'count': 0}
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo',
            })

            task.init(job_config)
            task._delete_stale_nodes()
            task._delete_stale_relations()

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': u'foo', 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.published_tag < $marker
            OR NOT EXISTS(target.published_tag))
            WITH target LIMIT $batch_size
            DETACH DELETE (target)
            RETURN count(*) as count
            """))

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': u'foo', 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.published_tag < $marker
            OR NOT EXISTS(target.published_tag))
            WITH target LIMIT $batch_size
            DELETE target
            RETURN count(*) as count
            """))

    def test_delete_statement_publish_tag_retain_data_with_no_publisher_metadata(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            mock_execute.return_value.single.return_value = {'count': 0}
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.RETAIN_DATA_WITH_NO_PUBLISHER_METADATA}': True
            })

            task.init(job_config)
            task._delete_stale_nodes()
            task._delete_stale_relations()

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': u'foo', 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.published_tag < $marker)
            WITH target LIMIT $batch_size
            DETACH DELETE (target)
            RETURN count(*) as count
            """))

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': u'foo', 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.published_tag < $marker)
            WITH target LIMIT $batch_size
            DELETE target
            RETURN count(*) as count
            """))

    def test_delete_statement_ms_to_expire(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            mock_execute.return_value.single.return_value = {'count': 0}
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.MS_TO_EXPIRE}': 9876543210
            })

            task.init(job_config)
            task._delete_stale_nodes()
            task._delete_stale_relations()

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': 9876543210, 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.publisher_last_updated_epoch_ms < (timestamp() - $marker)
            OR NOT EXISTS(target.publisher_last_updated_epoch_ms))
            WITH target LIMIT $batch_size
            DETACH DELETE (target)
            RETURN count(*) as count
            """))

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': 9876543210, 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.publisher_last_updated_epoch_ms < (timestamp() - $marker)
            OR NOT EXISTS(target.publisher_last_updated_epoch_ms))
            WITH target LIMIT $batch_size
            DELETE target
            RETURN count(*) as count
            """))

    def test_delete_statement_ms_to_expire_retain_data_with_no_publisher_metadata(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            mock_execute.return_value.single.return_value = {'count': 0}
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.MS_TO_EXPIRE}': 9876543210,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.RETAIN_DATA_WITH_NO_PUBLISHER_METADATA}': True
            })

            task.init(job_config)
            task._delete_stale_nodes()
            task._delete_stale_relations()

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': 9876543210, 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.publisher_last_updated_epoch_ms < (timestamp() - $marker))
            WITH target LIMIT $batch_size
            DETACH DELETE (target)
            RETURN count(*) as count
            """))

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': 9876543210, 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.publisher_last_updated_epoch_ms < (timestamp() - $marker))
            WITH target LIMIT $batch_size
            DELETE target
            RETURN count(*) as count
            """))

    def test_delete_statement_with_target_condition(self) -> None:
        with patch.object(GraphDatabase, 'driver'), patch.object(Neo4jStalenessRemovalTask, '_execute_cypher_query') \
                as mock_execute:
            mock_execute.return_value.single.return_value = {'count': 0}
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': [TargetWithCondition('Foo', '(target)-[:BAR]->(:Foo) AND target.name=\'foo_name\'')],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': [TargetWithCondition('BAR', '(start_node:Foo)-[target]->(end_node:Foo)')],
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo',
            })

            task.init(job_config)
            task._delete_stale_nodes()
            task._delete_stale_relations()

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': u'foo', 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (target:Foo)
            WHERE (target.published_tag < $marker
            OR NOT EXISTS(target.published_tag)) AND (target)-[:BAR]->(:Foo) AND target.name=\'foo_name\'
            WITH target LIMIT $batch_size
            DETACH DELETE (target)
            RETURN count(*) as count
            """))

            mock_execute.assert_any_call(dry_run=False,
                                         param_dict={'marker': u'foo', 'batch_size': 100},
                                         statement=textwrap.dedent("""
            MATCH (start_node)-[target:BAR]-(end_node)
            WHERE (target.published_tag < $marker
            OR NOT EXISTS(target.published_tag)) AND (start_node:Foo)-[target]->(end_node:Foo)
            WITH target LIMIT $batch_size
            DELETE target
            RETURN count(*) as count
            """))

    def test_ms_to_expire_too_small(self) -> None:
        with patch.object(GraphDatabase, 'driver'):
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.MS_TO_EXPIRE}': 24 * 60 * 60 * 100 - 10
            })

            try:
                task.init(job_config)
                self.assertTrue(False, 'Should have failed with small TTL   ')
            except Exception:
                pass

        with patch.object(GraphDatabase, 'driver'):
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.MS_TO_EXPIRE}': 24 * 60 * 60 * 1000,
            })
            task.init(job_config)

    def test_delete_dry_run(self) -> None:
        with patch.object(GraphDatabase, 'driver') as mock_driver:
            session_mock = mock_driver.return_value.session

            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                f'job.identifier': 'remove_stale_data_job',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_END_POINT_KEY}': 'foobar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_USER}': 'foo',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.NEO4J_PASSWORD}': 'bar',
                f'{task.get_scope()}.{neo4j_staleness_removal_task.STALENESS_MAX_PCT}': 5,
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_NODES}': ['Foo'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.TARGET_RELATIONS}': ['BAR'],
                f'{task.get_scope()}.{neo4j_staleness_removal_task.DRY_RUN}': True,
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo',
            })

            task.init(job_config)
            task._delete_stale_nodes()
            task._delete_stale_relations()

            session_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
