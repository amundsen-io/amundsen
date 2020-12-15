# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import re
from collections import namedtuple
from datetime import date, timedelta
from time import sleep
from typing import (
    Any, Dict, Iterator, List, Optional, Tuple,
)

from pyhocon import ConfigTree

from databuilder.extractor.base_bigquery_extractor import BaseBigQueryExtractor

TableColumnUsageTuple = namedtuple('TableColumnUsageTuple', ['database', 'cluster', 'schema',
                                                             'table', 'column', 'email'])

LOGGER = logging.getLogger(__name__)


class BigQueryTableUsageExtractor(BaseBigQueryExtractor):
    """
    An aggregate extractor for bigquery table usage. This class takes the data from
    the stackdriver logging API by filtering on timestamp, bigquery_resource and looking
    for referencedTables in the response.
    """
    TIMESTAMP_KEY = 'timestamp'
    _DEFAULT_SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
    EMAIL_PATTERN = 'email_pattern'
    DELAY_TIME = 'delay_time'

    def init(self, conf: ConfigTree) -> None:
        BaseBigQueryExtractor.init(self, conf)
        self.timestamp = conf.get_string(
            BigQueryTableUsageExtractor.TIMESTAMP_KEY,
            (date.today() - timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z'))

        self.email_pattern = conf.get_string(BigQueryTableUsageExtractor.EMAIL_PATTERN, None)
        self.delay_time = conf.get_int(BigQueryTableUsageExtractor.DELAY_TIME, 100)

        self.table_usage_counts: Dict[TableColumnUsageTuple, int] = {}
        self._count_usage()
        self.iter = iter(self.table_usage_counts)

    def _count_usage(self) -> None:  # noqa: C901
        count = 0
        for entry in self._retrieve_records():
            count += 1
            if count % self.pagesize == 0:
                LOGGER.info(f'Aggregated %i records', count)

            if entry is None:
                continue

            try:
                job = entry['protoPayload']['serviceData']['jobCompletedEvent']['job']
            except Exception:
                continue
            if job['jobStatus']['state'] != 'DONE':
                # This job seems not to have finished yet, so we ignore it.
                continue
            if len(job['jobStatus'].get('error', {})) > 0:
                # This job has errors, so we ignore it
                continue

            email = entry['protoPayload']['authenticationInfo']['principalEmail']
            # Query results can be cached and if the source tables remain untouched,
            # bigquery will return it from a 24 hour cache result instead. In that
            # case, referencedTables has been observed to be empty:
            # https://cloud.google.com/logging/docs/reference/audit/bigquery/rest/Shared.Types/AuditData#JobStatistics

            refTables = job['jobStatistics'].get('referencedTables', None)
            if refTables:
                if 'totalTablesProcessed' in job['jobStatistics']:
                    self._create_records(
                        refTables,
                        job['jobStatistics']['totalTablesProcessed'], email,
                        job['jobName']['jobId'])

            refViews = job['jobStatistics'].get('referencedViews', None)
            if refViews:
                if 'totalViewsProcessed' in job['jobStatistics']:
                    self._create_records(
                        refViews, job['jobStatistics']['totalViewsProcessed'],
                        email, job['jobName']['jobId'])

    def _create_records(self, refResources: List[dict], resourcesProcessed: int, email: str,
                        jobId: str) -> None:
        # if email filter is provided, only the email matched with filter will be recorded.
        if self.email_pattern:
            if not re.match(self.email_pattern, email):
                # the usage account not match email pattern
                return

        if len(refResources) != resourcesProcessed:
            LOGGER.warning(f'The number of tables listed in job {jobId} is not consistent')
            return

        for refResource in refResources:
            key = TableColumnUsageTuple(database='bigquery',
                                        cluster=refResource['projectId'],
                                        schema=refResource['datasetId'],
                                        table=refResource['tableId'],
                                        column='*',
                                        email=email)

            new_count = self.table_usage_counts.get(key, 0) + 1
            self.table_usage_counts[key] = new_count

    def _retrieve_records(self) -> Iterator[Optional[Dict]]:
        """
        Extracts bigquery log data by looking at the principalEmail in the
        authenticationInfo block and referencedTables in the jobStatistics.

        :return: Provides a record or None if no more to extract
        """
        body = {
            'resourceNames': [f'projects/{self.project_id}'],
            'pageSize': self.pagesize,
            'filter': 'resource.type="bigquery_resource" AND '
                      'protoPayload.methodName="jobservice.jobcompleted" AND '
                      f'timestamp >= "{self.timestamp}"'
        }
        for page in self._page_over_results(body):
            for entry in page['entries']:
                yield entry

    def extract(self) -> Optional[Tuple[Any, int]]:
        try:
            key = next(self.iter)
            return key, self.table_usage_counts[key]
        except StopIteration:
            return None

    def _page_over_results(self, body: Dict) -> Iterator[Dict]:
        response = self.logging_service.entries().list(body=body).execute(
            num_retries=BigQueryTableUsageExtractor.NUM_RETRIES)
        while response:
            if 'entries' in response:
                yield response

            try:
                if 'nextPageToken' in response:
                    body['pageToken'] = response['nextPageToken']
                    response = self.logging_service.entries().list(body=body).execute(
                        num_retries=BigQueryTableUsageExtractor.NUM_RETRIES)
                else:
                    response = None
            except Exception:
                # Add a delay when BQ quota exceeds limitation
                sleep(self.delay_time)

    def get_scope(self) -> str:
        return 'extractor.bigquery_table_usage'
