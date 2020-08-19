# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from collections import namedtuple

import google.oauth2.service_account
import google_auth_httplib2
from googleapiclient.discovery import build
import httplib2
from pyhocon import ConfigTree
from typing import Any, Dict, Iterator, List

from databuilder.extractor.base_extractor import Extractor


DatasetRef = namedtuple('DatasetRef', ['datasetId', 'projectId'])
TableKey = namedtuple('TableKey', ['schema', 'table_name'])

LOGGER = logging.getLogger(__name__)


class BaseBigQueryExtractor(Extractor):
    PROJECT_ID_KEY = 'project_id'
    KEY_PATH_KEY = 'key_path'
    # sometimes we don't have a key path, but only have an variable
    CRED_KEY = 'project_cred'
    PAGE_SIZE_KEY = 'page_size'
    FILTER_KEY = 'filter'
    _DEFAULT_SCOPES = ['https://www.googleapis.com/auth/bigquery.readonly']
    DEFAULT_PAGE_SIZE = 300
    NUM_RETRIES = 3
    DATE_LENGTH = 8

    def init(self, conf: ConfigTree) -> None:
        # should use key_path, or cred_key if the former doesn't exist
        self.key_path = conf.get_string(BaseBigQueryExtractor.KEY_PATH_KEY, None)
        self.cred_key = conf.get_string(BaseBigQueryExtractor.CRED_KEY, None)
        self.project_id = conf.get_string(BaseBigQueryExtractor.PROJECT_ID_KEY)
        self.pagesize = conf.get_int(
            BaseBigQueryExtractor.PAGE_SIZE_KEY,
            BaseBigQueryExtractor.DEFAULT_PAGE_SIZE)
        self.filter = conf.get_string(BaseBigQueryExtractor.FILTER_KEY, '')

        if self.key_path:
            credentials = (
                google.oauth2.service_account.Credentials.from_service_account_file(
                    self.key_path, scopes=self._DEFAULT_SCOPES))
        else:
            if self.cred_key:
                service_account_info = json.loads(self.cred_key)
                credentials = (
                    google.oauth2.service_account.Credentials.from_service_account_info(
                        service_account_info, scopes=self._DEFAULT_SCOPES))
            else:
                # FIXME: mypy can't find this attribute
                google_auth: Any = getattr(google, 'auth')
                credentials, _ = google_auth.default(scopes=self._DEFAULT_SCOPES)

        http = httplib2.Http()
        authed_http = google_auth_httplib2.AuthorizedHttp(credentials, http=http)
        self.bigquery_service = build('bigquery', 'v2', http=authed_http, cache_discovery=False)
        self.logging_service = build('logging', 'v2', http=authed_http, cache_discovery=False)
        self.iter: Iterator[Any] = iter([])

    def extract(self) -> Any:
        try:
            return next(self.iter)
        except StopIteration:
            return None

    def _is_sharded_table(self, table_id: str) -> bool:
        suffix = table_id[-BaseBigQueryExtractor.DATE_LENGTH:]
        return suffix.isdigit()

    def _iterate_over_tables(self) -> Any:
        for dataset in self._retrieve_datasets():
            for entry in self._retrieve_tables(dataset):
                yield entry

    # TRICKY: this function has different return types between different subclasses,
    # so type as Any. Should probably refactor to remove this unclear sharing.
    def _retrieve_tables(self, dataset: DatasetRef) -> Any:
        pass

    def _retrieve_datasets(self) -> List[DatasetRef]:
        datasets = []
        for page in self._page_dataset_list_results():
            if 'datasets' not in page:
                continue

            for dataset in page['datasets']:
                dataset_ref = dataset['datasetReference']
                ref = DatasetRef(**dataset_ref)
                datasets.append(ref)

        return datasets

    def _page_dataset_list_results(self) -> Iterator[Any]:
        response = self.bigquery_service.datasets().list(
            projectId=self.project_id,
            all=False,  # Do not return hidden datasets
            filter=self.filter,
            maxResults=self.pagesize).execute(
                num_retries=BaseBigQueryExtractor.NUM_RETRIES)

        while response:
            yield response

            if 'nextPageToken' in response:
                response = self.bigquery_service.datasets().list(
                    projectId=self.project_id,
                    all=True,
                    filter=self.filter,
                    pageToken=response['nextPageToken']).execute(
                        num_retries=BaseBigQueryExtractor.NUM_RETRIES)
            else:
                response = None

    def _page_table_list_results(self, dataset: DatasetRef) -> Iterator[Dict[str, Any]]:
        response = self.bigquery_service.tables().list(
            projectId=dataset.projectId,
            datasetId=dataset.datasetId,
            maxResults=self.pagesize).execute(
                num_retries=BaseBigQueryExtractor.NUM_RETRIES)

        while response:
            yield response

            if 'nextPageToken' in response:
                response = self.bigquery_service.tables().list(
                    projectId=dataset.projectId,
                    datasetId=dataset.datasetId,
                    maxResults=self.pagesize,
                    pageToken=response['nextPageToken']).execute(
                        num_retries=BaseBigQueryExtractor.NUM_RETRIES)
            else:
                response = None

    def get_scope(self) -> str:
        return 'extractor.bigquery_table_metadata'
