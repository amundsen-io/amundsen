# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import six
from collections import namedtuple

from pyhocon import ConfigFactory, ConfigTree  # noqa: F401
from typing import Iterator, Union, Dict, Any  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata
from itertools import groupby

TableKey = namedtuple('TableKey', ['schema_name', 'table_name'])

LOGGER = logging.getLogger(__name__)


class MSSQLMetadataExtractor(Extractor):
    """
    Extracts Microsoft SQL Server table and column metadata from underlying
    meta store database using SQLAlchemyExtractor
    """

    # SELECT statement from MS SQL to extract table and column metadata
    SQL_STATEMENT = """
        SELECT DISTINCT
            {cluster_source} AS cluster,
            TBL.TABLE_SCHEMA AS [schema_name],
            TBL.TABLE_NAME AS [name],
            CAST(PROP.VALUE AS NVARCHAR(MAX)) AS [description],
            COL.COLUMN_NAME AS [col_name],
            COL.DATA_TYPE AS [col_type],
            CAST(PROP_COL.VALUE AS NVARCHAR(MAX)) AS [col_description],
            COL.ORDINAL_POSITION AS col_sort_order
        FROM INFORMATION_SCHEMA.TABLES TBL
        INNER JOIN INFORMATION_SCHEMA.COLUMNS COL
            ON (COL.TABLE_NAME = TBL.TABLE_NAME
                AND COL.TABLE_SCHEMA = TBL.TABLE_SCHEMA )
        LEFT JOIN SYS.EXTENDED_PROPERTIES PROP
            ON (PROP.MAJOR_ID = OBJECT_ID(TBL.TABLE_SCHEMA + '.' + TBL.TABLE_NAME)
                AND PROP.MINOR_ID = 0
                AND PROP.NAME = 'MS_Description')
        LEFT JOIN SYS.EXTENDED_PROPERTIES PROP_COL
            ON (PROP_COL.MAJOR_ID = OBJECT_ID(TBL.TABLE_SCHEMA + '.' + TBL.TABLE_NAME)
                AND PROP_COL.MINOR_ID = COL.ORDINAL_POSITION
                AND PROP_COL.NAME = 'MS_Description')
        WHERE TBL.TABLE_TYPE = 'base table' {where_clause_suffix}
        ORDER BY
            CLUSTER,
            SCHEMA_NAME,
            NAME,
            COL_SORT_ORDER
        ;
    """

    # CONFIG KEYS
    WHERE_CLAUSE_SUFFIX_KEY = 'where_clause_suffix'
    CLUSTER_KEY = 'cluster_key'
    USE_CATALOG_AS_CLUSTER_NAME = 'use_catalog_as_cluster_name'
    DATABASE_KEY = 'database_key'

    # Default values
    DEFAULT_CLUSTER_NAME = 'DB_NAME()'

    DEFAULT_CONFIG = ConfigFactory.from_dict({
        WHERE_CLAUSE_SUFFIX_KEY: '',
        CLUSTER_KEY: DEFAULT_CLUSTER_NAME,
        USE_CATALOG_AS_CLUSTER_NAME: True}
    )

    DEFAULT_WHERE_CLAUSE_VALUE = 'and tbl.table_schema in {schemas}'

    def init(self, conf):
        # type: (ConfigTree) -> None
        conf = conf.with_fallback(MSSQLMetadataExtractor.DEFAULT_CONFIG)

        self._cluster = '{}'.format(
            conf.get_string(MSSQLMetadataExtractor.CLUSTER_KEY))

        if conf.get_bool(MSSQLMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME):
            cluster_source = "DB_NAME()"
        else:
            cluster_source = "'{}'".format(self._cluster)

        database = conf.get_string(
            MSSQLMetadataExtractor.DATABASE_KEY,
            default='mssql')
        if six.PY2 and isinstance(database, six.text_type):
            database = database.encode('utf-8', 'ignore')

        self._database = database

        config_where_clause = conf.get_string(
            MSSQLMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY)

        logging.info("Crawling for Schemas %s", config_where_clause)

        if len(config_where_clause) > 0:
            where_clause_suffix = MSSQLMetadataExtractor\
                .DEFAULT_WHERE_CLAUSE_VALUE\
                .format(schemas=config_where_clause)
        else:
            where_clause_suffix = ''

        self.sql_stmt = MSSQLMetadataExtractor.SQL_STATEMENT.format(
            where_clause_suffix=where_clause_suffix,
            cluster_source=cluster_source
        )

        LOGGER.info('SQL for MS SQL Metadata: {}'.format(self.sql_stmt))

        self._alchemy_extractor = SQLAlchemyExtractor()
        sql_alch_conf = Scoped\
            .get_scoped_conf(conf, self._alchemy_extractor.get_scope()) \
            .with_fallback(
                ConfigFactory.from_dict({
                    SQLAlchemyExtractor.EXTRACT_SQL: self.sql_stmt})
            )

        self._alchemy_extractor.init(sql_alch_conf)
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
        return 'extractor.mssql_metadata'

    def _get_extract_iter(self):
        # type: () -> Iterator[TableMetadata]
        """
        Using itertools.groupby and raw level iterator,
        it groups to table and yields TableMetadata
        :return:
        """
        for key, group in groupby(self._get_raw_extract_iter(), self._get_table_key):
            columns = []

            for row in group:
                last_row = row
                columns.append(
                    ColumnMetadata(
                        row['col_name'],
                        row['col_description'],
                        row['col_type'],
                        row['col_sort_order']))

            yield TableMetadata(
                self._database,
                last_row['cluster'],
                last_row['schema_name'],
                last_row['name'],
                last_row['description'],
                columns,
                tags=last_row['schema_name'])

    def _get_raw_extract_iter(self):
        # type: () -> Iterator[Dict[str, Any]]
        """
        Provides iterator of result row from SQLAlchemy extractor
        :return:
        """
        row = self._alchemy_extractor.extract()
        while row:
            yield row
            row = self._alchemy_extractor.extract()

    def _get_table_key(self, row):
        # type: (Dict[str, Any]) -> Union[TableKey, None]
        """
        Table key consists of schema and table name
        :param row:
        :return:
        """
        if row:
            return TableKey(
                schema_name=row['schema_name'],
                table_name=row['name'])

        return None
