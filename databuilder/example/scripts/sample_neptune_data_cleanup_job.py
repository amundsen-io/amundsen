# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

"""
Shows how to set up a job that uses the neptune neptune staleness removal task
"""
import logging
import os

from pyhocon import ConfigFactory

from databuilder.clients.neptune_client import NeptuneSessionClient
from databuilder.job.job import DefaultJob
from databuilder.task.neptune_staleness_removal_task import NeptuneStalenessRemovalTask


def create_remove_stale_data_job():
    logging.basicConfig(level=logging.INFO)
    access_key = os.getenv('AWS_KEY')
    access_secret = os.getenv('AWS_SECRET_KEY')
    aws_zone = os.getenv("AWS_ZONE")
    neptune_host = os.getenv('CREDENTIALS_NEPTUNE_HOST', 'localhost')
    neptune_port = os.getenv('CREDENTIALS_NEPTUNE_PORT', 7687)
    neptune_host = '{}:{}'.format(neptune_host, neptune_port)
    target_relations = ['DESCRIPTION', 'DESCRIPTION_OF', 'COLUMN', 'COLUMN_OF', 'TABLE', 'TABLE_OF']
    target_nodes = ['Table', 'Column', 'Programmatic_Description', "Schema"]
    job_config = ConfigFactory.from_dict({
        'task.remove_stale_data': {
            NeptuneStalenessRemovalTask.TARGET_RELATIONS: target_relations,
            NeptuneStalenessRemovalTask.TARGET_NODES: target_nodes,
            NeptuneStalenessRemovalTask.STALENESS_CUT_OFF_IN_SECONDS: 86400,  # 1 day
            'neptune.client': {
                NeptuneSessionClient.NEPTUNE_HOST_NAME: neptune_host,
                NeptuneSessionClient.AWS_REGION: aws_zone,
                NeptuneSessionClient.AWS_ACCESS_KEY: access_key,
                NeptuneSessionClient.AWS_SECRET_ACCESS_KEY: access_secret
            }
        }
    })
    job = DefaultJob(
        conf=job_config,
        task=NeptuneStalenessRemovalTask()
    )
    return job


if __name__ == '__main__':
    job = create_remove_stale_data_job()
    job.launch()
