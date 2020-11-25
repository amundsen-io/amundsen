# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

"""
This is a example script for extracting Feast feature tables
"""

from databuilder.extractor.feast_extractor import FeastExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.task.task import DefaultTask
from pyhocon import ConfigFactory

# NEO4J cluster endpoints
NEO4J_ENDPOINT = 'bolt://localhost:7687/'

neo4j_endpoint = NEO4J_ENDPOINT
neo4j_user = 'neo4j'
neo4j_password = 'test'

FEAST_ENDPOINT = 'feast-core.featurestore.svc.cluster.local:6565'

feast_endpoint = FEAST_ENDPOINT


def create_feast_job_config():
    tmp_folder = '/var/tmp/amundsen/table_metadata'
    node_files_folder = '{tmp_folder}/nodes/'.format(tmp_folder=tmp_folder)
    relationship_files_folder = '{tmp_folder}/relationships/'.format(tmp_folder=tmp_folder)

    job_config = ConfigFactory.from_dict({
        'extractor.feast.{}'.format(FeastExtractor.FEAST_ENDPOINT_CONFIG_KEY): feast_endpoint,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH):
            node_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH):
            relationship_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NODE_FILES_DIR):
            node_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.RELATION_FILES_DIR):
            relationship_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_END_POINT_KEY):
            neo4j_endpoint,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_USER):
            neo4j_user,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_PASSWORD):
            neo4j_password,
        'publisher.neo4j.job_publish_tag':
            'some_unique_tag'  # TO-DO unique tag must be added
    })
    return job_config


if __name__ == "__main__":
    job = DefaultJob(conf=create_feast_job_config(),
                     task=DefaultTask(extractor=FeastExtractor(), loader=FsNeo4jCSVLoader()),
                     publisher=neo4j_csv_publisher.Neo4jCsvPublisher())
    job.launch()
