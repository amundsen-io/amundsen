# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0


import logging
from collections import namedtuple
from itertools import groupby
from typing import (
    Any, Dict, Iterator, Union,
)

from pyhocon import ConfigFactory, ConfigTree

from databuilder.extractor import sql_alchemy_extractor
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.table_metadata_constants import PARTITION_BADGE
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata

TableKey = namedtuple('TableKey', ['schema', 'table_name'])

LOGGER = logging.getLogger(__name__)


class BigQueryMetadataExtractor(Extractor):
    """
    Extracts BigQuery table and column metadata from underlying meta store database using SQLAlchemyExtractor.
    Requirements:
        sqlalchemy-bigquery
    """
    # SELECT statement from bigquery information_schema to extract table and column metadata
    # https://cloud.google.com/bigquery/docs/information-schema-tables
    SQL_STATEMENT = """
        SELECT
            lower(c.COLUMN_NAME) AS col_name,
            cfp.DESCRIPTION AS col_description,
            lower(c.DATA_TYPE) AS col_type,
            ifnull(c.ORDINAL_POSITION, 0) AS col_sort_order,
            'bigquery' AS database,
            lower(c.TABLE_CATALOG) AS cluster,
            lower(c.TABLE_SCHEMA) AS schema,
            lower(c.TABLE_NAME) AS name,
            tops.OPTION_VALUE AS description,
            CASE c.IS_PARTITIONING_COLUMN WHEN 'YES' THEN 1 WHEN 'NO' THEN 0 ELSE NULL END AS is_partition_col,
            CASE WHEN t.TABLE_TYPE = 'VIEW' THEN 'true' ELSE 'false' END AS is_view
        FROM `{project}.{table_schema}.{schema}`.COLUMNS c
        LEFT JOIN `{project}.{table_schema}.{schema}`.TABLES t
            ON  c.TABLE_CATALOG = t.TABLE_CATALOG
            AND c.TABLE_SCHEMA  = t.TABLE_SCHEMA
            AND c.TABLE_NAME    = t.TABLE_NAME
        LEFT JOIN `{project}.{table_schema}.{schema}`.TABLE_OPTIONS tops
            ON  c.TABLE_CATALOG = tops.TABLE_CATALOG
            AND c.TABLE_SCHEMA  = tops.TABLE_SCHEMA
            AND c.TABLE_NAME    = tops.TABLE_NAME
            AND tops.OPTION_NAME = 'description'
        LEFT JOIN `{project}.{table_schema}.{schema}`.COLUMN_FIELD_PATHS cfp
            ON  c.TABLE_CATALOG = cfp.TABLE_CATALOG
            AND c.TABLE_SCHEMA  = cfp.TABLE_SCHEMA
            AND c.TABLE_NAME    = cfp.TABLE_NAME
            AND c.COLUMN_NAME   = cfp.COLUMN_NAME
        {where_clause_suffix};
    """

    # CONFIG KEYS
    WHERE_CLAUSE_SUFFIX_KEY = 'where_clause_suffix'
    CLUSTER_KEY = 'cluster_key'
    USE_CATALOG_AS_CLUSTER_NAME = 'use_catalog_as_cluster_name'
    # Database Key, used to identify the database type in the UI.
    DATABASE_KEY = 'database_key'
    # Bigquery Database Key, used to determine which Bigquery database to connect to.
    BIGQUERY_PROJECT_KEY = 'bigquery_project'
    # Bigquery Schema Key, used to determine which Bigquery schema to use.
    BIGQUERY_TABLE_SCHEMA_KEY = 'bigquery_table_schema'
    BIGQUERY_SCHEMA_KEY = 'bigquery_schema'

    # Default values
    DEFAULT_CLUSTER_NAME = 'master'

    DEFAULT_CONFIG = ConfigFactory.from_dict(
        {WHERE_CLAUSE_SUFFIX_KEY: ' ',
         CLUSTER_KEY: DEFAULT_CLUSTER_NAME,
         USE_CATALOG_AS_CLUSTER_NAME: True,
         DATABASE_KEY: 'bigquery',
         BIGQUERY_PROJECT_KEY: 'bigquery-public-data',
         BIGQUERY_TABLE_SCHEMA_KEY: 'samples',
         BIGQUERY_SCHEMA_KEY: 'INFORMATION_SCHEMA'}
    )

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(BigQueryMetadataExtractor.DEFAULT_CONFIG)
        self._cluster = conf.get_string(BigQueryMetadataExtractor.CLUSTER_KEY)

        if conf.get_bool(BigQueryMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME):
            cluster_source = "TABLE_CATALOG"
        else:
            cluster_source = f"'{self._cluster}'"

        self._database = conf.get_string(BigQueryMetadataExtractor.DATABASE_KEY)
        self._schema = conf.get_string(BigQueryMetadataExtractor.DATABASE_KEY)
        self._bigquery_project = conf.get_string(BigQueryMetadataExtractor.BIGQUERY_PROJECT_KEY)
        self._bigquery_table_schema = conf.get_string(BigQueryMetadataExtractor.BIGQUERY_TABLE_SCHEMA_KEY)
        self._bigquery_schema = conf.get_string(BigQueryMetadataExtractor.BIGQUERY_SCHEMA_KEY)

        self.sql_stmt = BigQueryMetadataExtractor.SQL_STATEMENT.format(
            where_clause_suffix=conf.get_string(BigQueryMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY),
            cluster_source=cluster_source,
            project=self._bigquery_project,
            table_schema=self._bigquery_table_schema,
            schema=self._bigquery_schema
        )

        LOGGER.info('SQL for bigquery metadata: %s', self.sql_stmt)

        self._alchemy_extractor = sql_alchemy_extractor.from_surrounding_config(conf, self.sql_stmt)
        self._extract_iter: Union[None, Iterator] = None

    def close(self) -> None:
        if getattr(self, '_alchemy_extractor', None) is not None:
            self._alchemy_extractor.close()

    def extract(self) -> Union[TableMetadata, None]:
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def get_scope(self) -> str:
        return 'extractor.bigquery'

    def _get_extract_iter(self) -> Iterator[TableMetadata]:
        """
        Using itertools.groupby and raw level iterator, it groups to table and yields TableMetadata
        :return:
        """
        for key, group in groupby(self._get_raw_extract_iter(), self._get_table_key):
            columns = []

            for row in group:
                last_row = row
                column = None
                if row['is_partition_col'] == 1:
                    # create add a badge to indicate partition column
                    column = ColumnMetadata(row['col_name'], row['col_description'],
                                            row['col_type'], row['col_sort_order'], [PARTITION_BADGE])
                else:
                    column = ColumnMetadata(row['col_name'], row['col_description'],
                                            row['col_type'], row['col_sort_order'])
                columns.append(column)
            is_view = last_row['is_view'] == 1
            yield TableMetadata('hive', self._cluster,
                                last_row['schema'],
                                last_row['name'],
                                last_row['description'],
                                columns,
                                is_view=is_view)

    def _get_raw_extract_iter(self) -> Iterator[Dict[str, Any]]:
        """
        Provides iterator of result row from SQLAlchemy extractor
        :return:
        """
        row = self._alchemy_extractor.extract()
        while row:
            yield row
            row = self._alchemy_extractor.extract()

    def _get_table_key(self, row: Dict[str, Any]) -> Union[TableKey, None]:
        """
        Table key consists of schema and table name
        :param row:
        :return:
        """
        if row:
            return TableKey(schema=row['schema'], table_name=row['name'])

        return None
