import logging
import unittest

from mock import patch
from neo4j.v1 import GraphDatabase
from pyhocon import ConfigFactory

from databuilder.publisher import neo4j_csv_publisher
from databuilder.task import neo4j_staleness_removal_task
from databuilder.task.neo4j_staleness_removal_task import Neo4jStalenessRemovalTask


class TestRemoveStaleData(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        logging.basicConfig(level=logging.INFO)

    def test_validation_failure(self):
        # type: () -> None

        with patch.object(GraphDatabase, 'driver'):
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                'job.identifier': 'remove_stale_data_job',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.NEO4J_END_POINT_KEY):
                    'foobar',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.NEO4J_USER):
                    'foo',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.NEO4J_PASSWORD):
                    'bar',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.STALENESS_MAX_PCT):
                    90,
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo'
            })

            task.init(job_config)
            total_records = [{'type': 'foo', 'count': 100}]
            stale_records = [{'type': 'foo', 'count': 50}]
            targets = {'foo'}
            task._validate_staleness_pct(total_records=total_records, stale_records=stale_records, types=targets)

    def test_validation(self):
        # type: () -> None

        with patch.object(GraphDatabase, 'driver'):
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                'job.identifier': 'remove_stale_data_job',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.NEO4J_END_POINT_KEY):
                    'foobar',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.NEO4J_USER):
                    'foo',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.NEO4J_PASSWORD):
                    'bar',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.STALENESS_MAX_PCT):
                    5,
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo'
            })

            task.init(job_config)
            total_records = [{'type': 'foo', 'count': 100}]
            stale_records = [{'type': 'foo', 'count': 50}]
            targets = {'foo'}
            self.assertRaises(Exception, task._validate_staleness_pct, total_records, stale_records, targets)

    def test_validation_threshold_override(self):
        # type: () -> None

        with patch.object(GraphDatabase, 'driver'):
            task = Neo4jStalenessRemovalTask()
            job_config = ConfigFactory.from_dict({
                'job.identifier': 'remove_stale_data_job',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.NEO4J_END_POINT_KEY):
                    'foobar',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.NEO4J_USER):
                    'foo',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.NEO4J_PASSWORD):
                    'bar',
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.STALENESS_MAX_PCT):
                    5,
                '{}.{}'.format(task.get_scope(), neo4j_staleness_removal_task.STALENESS_PCT_MAX_DICT):
                    {'foo': 51},
                neo4j_csv_publisher.JOB_PUBLISH_TAG: 'foo'
            })

            task.init(job_config)
            total_records = [{'type': 'foo', 'count': 100},
                             {'type': 'bar', 'count': 100}]
            stale_records = [{'type': 'foo', 'count': 50},
                             {'type': 'bar', 'count': 3}]
            targets = {'foo', 'bar'}
            task._validate_staleness_pct(total_records=total_records, stale_records=stale_records, types=targets)


if __name__ == '__main__':
    unittest.main()
