# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from collections import namedtuple

from pyhocon import ConfigTree  # noqa: F401
from typing import List, Any  # noqa: F401

from databuilder.extractor.base_bigquery_extractor import BaseBigQueryExtractor
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata


DatasetRef = namedtuple('DatasetRef', ['datasetId', 'projectId'])
TableKey = namedtuple('TableKey', ['schema', 'table_name'])

LOGGER = logging.getLogger(__name__)


class BigQueryMetadataExtractor(BaseBigQueryExtractor):

    """ A metadata extractor for bigquery tables, taking the schema metadata
    from the google cloud bigquery API's. This extractor goes through all visible
    datasets in the project identified by project_id and iterates over all tables
    it finds. A separate account is configurable through the key_path parameter,
    which should point to a valid json file corresponding to a service account.

    This extractor supports nested columns, which are delimited by a dot (.) in the
    column name.
    """

    def init(self, conf):
        # type: (ConfigTree) -> None
        BaseBigQueryExtractor.init(self, conf)
        self.grouped_tables = set([])

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
                if self._is_sharded_table(table_id):
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
                cols = []
                # Not all tables have schemas
                if 'schema' in table:
                    schema = table['schema']
                    if 'fields' in schema:
                        total_cols = 0
                        for column in schema['fields']:
                            total_cols = self._iterate_over_cols('', column, cols, total_cols + 1)

                table_meta = TableMetadata(
                    database='bigquery',
                    cluster=tableRef['projectId'],
                    schema=tableRef['datasetId'],
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

    def get_scope(self):
        # type: () -> str
        return 'extractor.bigquery_table_metadata'
