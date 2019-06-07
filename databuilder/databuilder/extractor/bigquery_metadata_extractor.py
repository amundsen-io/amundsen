import logging
from collections import namedtuple

import google.oauth2.service_account
import google_auth_httplib2
from googleapiclient.discovery import build
import httplib2
from pyhocon import ConfigTree  # noqa: F401
from typing import List, Any  # noqa: F401

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata


DatasetRef = namedtuple('DatasetRef', ['datasetId', 'projectId'])
TableKey = namedtuple('TableKey', ['schema_name', 'table_name'])

LOGGER = logging.getLogger(__name__)


class BigQueryMetadataExtractor(Extractor):

    """ A metadata extractor for bigquery tables, taking the schema metadata
    from the google cloud bigquery API's. This extractor goes through all visible
    datasets in the project identified by project_id and iterates over all tables
    it finds. A separate account is configurable through the key_path parameter,
    which should point to a valid json file corresponding to a service account.

    This extractor supports nested columns, which are delimited by a dot (.) in the
    column name.
    """

    PROJECT_ID_KEY = 'project_id'
    KEY_PATH_KEY = 'key_path'
    PAGE_SIZE_KEY = 'page_size'
    FILTER_KEY = 'filter'
    _DEFAULT_SCOPES = ['https://www.googleapis.com/auth/bigquery.readonly', ]
    DEFAULT_PAGE_SIZE = 300
    NUM_RETRIES = 3
    DATE_LENGTH = 8

    def init(self, conf):
        # type: (ConfigTree) -> None
        self.key_path = conf.get_string(BigQueryMetadataExtractor.KEY_PATH_KEY, None)
        self.project_id = conf.get_string(BigQueryMetadataExtractor.PROJECT_ID_KEY)
        self.pagesize = conf.get_int(
            BigQueryMetadataExtractor.PAGE_SIZE_KEY,
            BigQueryMetadataExtractor.DEFAULT_PAGE_SIZE)
        self.filter = conf.get_string(BigQueryMetadataExtractor.FILTER_KEY, '')

        if self.key_path:
            credentials = (
                google.oauth2.service_account.Credentials.from_service_account_file(
                    self.key_path, scopes=BigQueryMetadataExtractor._DEFAULT_SCOPES))
        else:
            credentials, _ = google.auth.default(scopes=BigQueryMetadataExtractor._DEFAULT_SCOPES)

        http = httplib2.Http()
        authed_http = google_auth_httplib2.AuthorizedHttp(credentials, http=http)
        self.bigquery_service = build('bigquery', 'v2', http=authed_http, cache_discovery=False)
        self.datasets = self._retrieve_datasets()
        self.iter = iter(self._iterate_over_tables())
        self.grouped_tables = set([])

    def extract(self):
        # type: () -> Any
        try:
            return next(self.iter)
        except StopIteration:
            return None

    def _iterate_over_tables(self):
        # type: () -> Any
        for dataset in self.datasets:
            for entry in self._retrieve_tables(dataset):
                yield(entry)

    def _retrieve_datasets(self):
        # type: () -> List[DatasetRef]
        datasets = []
        for page in self._page_dataset_list_results():
            if 'datasets' not in page:
                continue

            for dataset in page['datasets']:
                dataset_ref = dataset['datasetReference']
                ref = DatasetRef(**dataset_ref)
                datasets.append(ref)

        return datasets

    def _page_dataset_list_results(self):
        # type: () -> Any
        response = self.bigquery_service.datasets().list(
            projectId=self.project_id,
            all=False,  # Do not return hidden datasets
            filter=self.filter,
            maxResults=self.pagesize).execute(
                num_retries=BigQueryMetadataExtractor.NUM_RETRIES)

        while response:
            yield response

            if 'nextPageToken' in response:
                response = self.bigquery_service.datasets().list(
                    projectId=self.project_id,
                    all=True,
                    filter=self.filter,
                    pageToken=response['nextPageToken']).execute(
                        num_retries=BigQueryMetadataExtractor.NUM_RETRIES)
            else:
                response = None

    def _retrieve_tables(self, dataset):
        # type: () -> Any
        for page in self._page_table_list_results(dataset):
            if 'tables' not in page:
                continue

            for table in page['tables']:
                tableRef = table['tableReference']

                table_id = tableRef['tableId']

                # BigQuery tables that have 8 digits as last characters are
                # considered date range tables and are grouped together in the UI.
                # ( e.g. ga_sessions_20190101, ga_sessions_20190102, etc. )
                last_eight_chars = table_id[-BigQueryMetadataExtractor.DATE_LENGTH:]
                if last_eight_chars.isdigit():
                    # If the last eight characters are digits, we assume the table is of a table date range type
                    # and then we only need one schema definition
                    table_prefix = table_id[:-BigQueryMetadataExtractor.DATE_LENGTH]
                    if table_prefix in self.grouped_tables:
                        # If one table in the date range is processed, then ignore other ones
                        # (it adds too much metadata)
                        continue

                    table_id = table_prefix
                    self.grouped_tables.add(table_prefix)

                table = self.bigquery_service.tables().get(
                    projectId=tableRef['projectId'],
                    datasetId=tableRef['datasetId'],
                    tableId=tableRef['tableId']).execute(num_retries=BigQueryMetadataExtractor.NUM_RETRIES)

                # BigQuery tables also have interesting metadata about partitioning
                # data location (EU/US), mod/create time, etc... Extract that some other time?
                schema = table['schema']
                cols = []
                if 'fields' in schema:
                    total_cols = 0
                    for column in schema['fields']:
                        total_cols = self._iterate_over_cols('', column, cols, total_cols + 1)

                table_meta = TableMetadata(
                    database='bigquery',
                    cluster=tableRef['projectId'],
                    schema_name=tableRef['datasetId'],
                    name=table_id,
                    description=table.get('description', ''),
                    columns=cols,
                    is_view=table['type'] == 'VIEW')

                yield(table_meta)

    def _iterate_over_cols(self, parent, column, cols, total_cols):
        # type: (str, str, List[ColumnMetadata()], int) -> int
        if len(parent) > 0:
            col_name = '{parent}.{field}'.format(parent=parent, field=column['name'])
        else:
            col_name = column['name']

        if column['type'] == 'RECORD':
            col = ColumnMetadata(
                name=col_name,
                description=column.get('description', ''),
                col_type=column['type'],
                sort_order=total_cols)
            cols.append(col)
            total_cols += 1
            for field in column['fields']:
                total_cols = self._iterate_over_cols(col_name, field, cols, total_cols)
            return total_cols
        else:
            col = ColumnMetadata(
                name=col_name,
                description=column.get('description', ''),
                col_type=column['type'],
                sort_order=total_cols)
            cols.append(col)
            return total_cols + 1

    def _page_table_list_results(self, dataset):
        # type: (DatasetRef) -> Any
        response = self.bigquery_service.tables().list(
            projectId=dataset.projectId,
            datasetId=dataset.datasetId,
            maxResults=self.pagesize).execute(
                num_retries=BigQueryMetadataExtractor.NUM_RETRIES)

        while response:
            yield response

            if 'nextPageToken' in response:
                response = self.bigquery_service.tables().list(
                    projectId=dataset.projectId,
                    datasetId=dataset.datasetId,
                    maxResults=self.pagesize,
                    pageToken=response['nextPageToken']).execute(
                        num_retries=BigQueryMetadataExtractor.NUM_RETRIES)
            else:
                response = None

    def get_scope(self):
        # type: () -> str
        return 'extractor.bigquery_table_metadata'
