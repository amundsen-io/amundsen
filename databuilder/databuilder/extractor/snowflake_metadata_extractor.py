# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0


import logging
from collections import namedtuple

from pyhocon import ConfigFactory, ConfigTree
from typing import Iterator, Union, Dict, Any
from unidecode import unidecode

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata
from itertools import groupby


TableKey = namedtuple('TableKey', ['schema', 'table_name'])

LOGGER = logging.getLogger(__name__)


class SnowflakeMetadataExtractor(Extractor):
    """
    Extracts Snowflake table and column metadata from underlying meta store database using SQLAlchemyExtractor.
    Requirements:
        snowflake-connector-python
        snowflake-sqlalchemy
    """
    # SELECT statement from snowflake information_schema to extract table and column metadata
    SQL_STATEMENT = """
    SELECT
        lower(c.column_name) AS col_name,
        c.comment AS col_description,
        lower(c.data_type) AS col_type,
        lower(c.ordinal_position) AS col_sort_order,
        lower(c.table_catalog) AS database,
        lower({cluster_source}) AS cluster,
        lower(c.table_schema) AS schema,
        lower(c.table_name) AS name,
        t.comment AS description,
        decode(lower(t.table_type), 'view', 'true', 'false') AS is_view
    FROM
        {database}.INFORMATION_SCHEMA.COLUMNS AS c
    LEFT JOIN
        {database}.INFORMATION_SCHEMA.TABLES t
            ON c.TABLE_NAME = t.TABLE_NAME
            AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
    {where_clause_suffix};
    """

    # CONFIG KEYS
    WHERE_CLAUSE_SUFFIX_KEY = 'where_clause_suffix'
    CLUSTER_KEY = 'cluster_key'
    USE_CATALOG_AS_CLUSTER_NAME = 'use_catalog_as_cluster_name'
    # Database Key, used to identify the database type in the UI.
    DATABASE_KEY = 'database_key'
    # Snowflake Database Key, used to determine which Snowflake database to connect to.
    SNOWFLAKE_DATABASE_KEY = 'snowflake_database'

    # Default values
    DEFAULT_CLUSTER_NAME = 'master'

    DEFAULT_CONFIG = ConfigFactory.from_dict(
        {WHERE_CLAUSE_SUFFIX_KEY: ' ',
         CLUSTER_KEY: DEFAULT_CLUSTER_NAME,
         USE_CATALOG_AS_CLUSTER_NAME: True,
         DATABASE_KEY: 'snowflake',
         SNOWFLAKE_DATABASE_KEY: 'prod'}
    )

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(SnowflakeMetadataExtractor.DEFAULT_CONFIG)
        self._cluster = '{}'.format(conf.get_string(SnowflakeMetadataExtractor.CLUSTER_KEY))

        if conf.get_bool(SnowflakeMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME):
            cluster_source = "c.table_catalog"
        else:
            cluster_source = "'{}'".format(self._cluster)

        self._database = conf.get_string(SnowflakeMetadataExtractor.DATABASE_KEY)
        self._snowflake_database = conf.get_string(SnowflakeMetadataExtractor.SNOWFLAKE_DATABASE_KEY)

        self.sql_stmt = SnowflakeMetadataExtractor.SQL_STATEMENT.format(
            where_clause_suffix=conf.get_string(SnowflakeMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY),
            cluster_source=cluster_source,
            database=self._snowflake_database
        )

        LOGGER.info('SQL for snowflake metadata: {}'.format(self.sql_stmt))

        self._alchemy_extractor = SQLAlchemyExtractor()
        sql_alch_conf = Scoped.get_scoped_conf(conf, self._alchemy_extractor.get_scope())\
            .with_fallback(ConfigFactory.from_dict({SQLAlchemyExtractor.EXTRACT_SQL: self.sql_stmt}))

        self._alchemy_extractor.init(sql_alch_conf)
        self._extract_iter: Union[None, Iterator] = None

    def extract(self) -> Union[TableMetadata, None]:
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def get_scope(self) -> str:
        return 'extractor.snowflake'

    def _get_extract_iter(self) -> Iterator[TableMetadata]:
        """
        Using itertools.groupby and raw level iterator, it groups to table and yields TableMetadata
        :return:
        """
        for key, group in groupby(self._get_raw_extract_iter(), self._get_table_key):
            columns = []

            for row in group:
                last_row = row
                columns.append(ColumnMetadata(
                               row['col_name'],
                               unidecode(row['col_description']) if row['col_description'] else None,
                               row['col_type'],
                               row['col_sort_order'])
                               )

            yield TableMetadata(self._database, last_row['cluster'],
                                last_row['schema'],
                                last_row['name'],
                                unidecode(last_row['description']) if last_row['description'] else None,
                                columns,
                                last_row['is_view'] == 'true')

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
