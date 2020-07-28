# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import boto3

from pyhocon import ConfigFactory, ConfigTree  # noqa: F401
from typing import Iterator, Union, Dict, Any  # noqa: F401

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata


class GlueExtractor(Extractor):
    """
    Extracts tables and columns metadata from AWS Glue metastore
    """

    CLUSTER_KEY = 'cluster'
    FILTER_KEY = 'filters'
    DEFAULT_CONFIG = ConfigFactory.from_dict({CLUSTER_KEY: 'gold', FILTER_KEY: None})

    def init(self, conf):
        conf = conf.with_fallback(GlueExtractor.DEFAULT_CONFIG)
        self._cluster = '{}'.format(conf.get_string(GlueExtractor.CLUSTER_KEY))
        self._filters = conf.get(GlueExtractor.FILTER_KEY)
        self._glue = boto3.client('glue')
        self._extract_iter = None  # type: Union[None, Iterator]

    def extract(self):
        # type: () -> Union[TableMetadata, None]
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def get_scope(self):
        # type: () -> str
        return 'extractor.glue'

    def _get_extract_iter(self):
        # type: () -> Iterator[TableMetadata]
        """
        It gets all tables and yields TableMetadata
        :return:
        """
        for row in self._get_raw_extract_iter():
            columns, i = [], 0

            for column in row['StorageDescriptor']['Columns'] \
                    + row.get('PartitionKeys', []):
                columns.append(ColumnMetadata(
                    column['Name'],
                    column['Comment'] if 'Comment' in column else None,
                    column['Type'],
                    i
                ))
                i += 1

            yield TableMetadata(
                'glue',
                self._cluster,
                row['DatabaseName'],
                row['Name'],
                row.get('Description') or row.get('Parameters', {}).get('comment'),
                columns,
                row.get('TableType') == 'VIRTUAL_VIEW',
            )

    def _get_raw_extract_iter(self):
        # type: () -> Iterator[Dict[str, Any]]
        """
        Provides iterator of results row from glue client
        :return:
        """
        tables = self._search_tables()
        return iter(tables)

    def _search_tables(self):
        tables = []
        kwargs = {}
        if self._filters is not None:
            kwargs['Filters'] = self._filters
        data = self._glue.search_tables(**kwargs)
        tables += data['TableList']
        while 'NextToken' in data:
            token = data['NextToken']
            kwargs['NextToken'] = token
            data = self._glue.search_tables(**kwargs)
            tables += data['TableList']
        return tables
