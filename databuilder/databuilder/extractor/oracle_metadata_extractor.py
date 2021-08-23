# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from collections import namedtuple
from itertools import groupby
from typing import (
    Any, Dict, Iterator, Union,
)

from pyhocon import ConfigFactory, ConfigTree

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata

TableKey = namedtuple('TableKey', ['schema', 'table_name'])

LOGGER = logging.getLogger(__name__)


class OracleMetadataExtractor(Extractor):
    """
    Extracts Oracle table and column metadata from underlying meta store database using SQLAlchemyExtractor
    """

    # CONFIG KEYS
    WHERE_CLAUSE_SUFFIX_KEY = 'where_clause_suffix'
    CLUSTER_KEY = 'cluster_key'
    DATABASE_KEY = 'database_key'

    # Default values
    DEFAULT_CLUSTER_NAME = 'master'

    DEFAULT_CONFIG = ConfigFactory.from_dict(
        {WHERE_CLAUSE_SUFFIX_KEY: ' ', CLUSTER_KEY: DEFAULT_CLUSTER_NAME}
    )

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(OracleMetadataExtractor.DEFAULT_CONFIG)
        self._cluster = conf.get_string(OracleMetadataExtractor.CLUSTER_KEY, default='oracle')

        self._database = conf.get_string(OracleMetadataExtractor.DATABASE_KEY, default='oracle')

        self.sql_stmt = self.get_sql_statement(
            where_clause_suffix=conf.get_string(OracleMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY),
        )

        self._alchemy_extractor = SQLAlchemyExtractor()
        sql_alch_conf = Scoped.get_scoped_conf(conf, self._alchemy_extractor.get_scope()) \
            .with_fallback(ConfigFactory.from_dict({SQLAlchemyExtractor.EXTRACT_SQL: self.sql_stmt}))

        self.sql_stmt = sql_alch_conf.get_string(SQLAlchemyExtractor.EXTRACT_SQL)

        LOGGER.info('SQL for oracle metadata: %s', self.sql_stmt)

        self._alchemy_extractor.init(sql_alch_conf)
        self._extract_iter: Union[None, Iterator] = None

    def extract(self) -> Union[TableMetadata, None]:
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def _get_extract_iter(self) -> Iterator[TableMetadata]:
        """
        Using itertools.groupby and raw level iterator, it groups to table and yields TableMetadata
        :return:
        """
        for key, group in groupby(self._get_raw_extract_iter(), self._get_table_key):
            columns = []

            for row in group:
                last_row = row
                columns.append(ColumnMetadata(row['col_name'], row['col_description'],
                                              row['col_type'], row['col_sort_order']))

            yield TableMetadata(self._database, last_row['cluster'],
                                last_row['schema'],
                                last_row['name'],
                                last_row['description'],
                                columns)

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

    def get_sql_statement(self, where_clause_suffix: str) -> str:
        cluster_source = f"'{self._cluster}'"

        return """
        SELECT
            {cluster_source} as "cluster",
            lower(c.owner) as "schema",
            lower(c.table_name) as "name",
            tc.comments as "description",
            lower(c.column_name) as "col_name",
            lower(c.data_type) as "col_type",
            cc.comments as "col_description",
            lower(c.column_id) as "col_sort_order"
        FROM
            all_tab_columns c
        LEFT JOIN
            all_tab_comments tc ON c.owner=tc.owner AND c.table_name=tc.table_name
        LEFT JOIN
            all_col_comments cc ON c.owner=cc.owner AND c.table_name=cc.table_name AND c.column_name=cc.column_name
        {where_clause_suffix}
        ORDER BY "cluster", "schema", "name", "col_sort_order"
        """.format(
            cluster_source=cluster_source,
            where_clause_suffix=where_clause_suffix,
        )

    def get_scope(self) -> str:
        return 'extractor.oracle_metadata'
