# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

# A modified version of `base_postgres_metadata_extractor` as an example of new changes
# The examples provided are for illustrative purposes only and will differ from the actual use case

import abc
import logging
from collections import namedtuple
from itertools import groupby
from typing import (
    Any, Dict, Iterator, Union,
)

from sqlalchemy import column

from pyhocon import ConfigFactory, ConfigTree

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata

TableKey = namedtuple('TableKey', ['schema', 'table_name'])

LOGGER = logging.getLogger(__name__)


class BasePostgresMetadataExtractor(Extractor):
    """
    Extracts Postgres table and column metadata from underlying meta store database using SQLAlchemyExtractor
    """

    # CONFIG KEYS
    WHERE_CLAUSE_SUFFIX_KEY = 'where_clause_suffix'
    CLUSTER_KEY = 'cluster_key'
    USE_CATALOG_AS_CLUSTER_NAME = 'use_catalog_as_cluster_name'
    DATABASE_KEY = 'database_key'

    # Default values
    DEFAULT_CLUSTER_NAME = 'master'

    DEFAULT_CONFIG = ConfigFactory.from_dict(
        {WHERE_CLAUSE_SUFFIX_KEY: 'true', CLUSTER_KEY: DEFAULT_CLUSTER_NAME, USE_CATALOG_AS_CLUSTER_NAME: True}
    )

    @abc.abstractmethod
    def get_sql_statement(self, use_catalog_as_cluster_name: bool, where_clause_suffix: str) -> Any:
        """
        :return: Provides a record or None if no more to extract
        """
        return None

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(BasePostgresMetadataExtractor.DEFAULT_CONFIG)
        self._cluster = conf.get_string(BasePostgresMetadataExtractor.CLUSTER_KEY)

        self._database = conf.get_string(BasePostgresMetadataExtractor.DATABASE_KEY, default='postgres')

        self.sql_stmt = self.get_sql_statement(
            use_catalog_as_cluster_name=conf.get_bool(BasePostgresMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME),
            where_clause_suffix=conf.get_string(BasePostgresMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY),
        )

        self._alchemy_extractor = SQLAlchemyExtractor()
        sql_alch_conf = Scoped.get_scoped_conf(conf, self._alchemy_extractor.get_scope())\
            .with_fallback(ConfigFactory.from_dict({SQLAlchemyExtractor.EXTRACT_SQL: self.sql_stmt}))

        self.sql_stmt = sql_alch_conf.get_string(SQLAlchemyExtractor.EXTRACT_SQL)

        LOGGER.info('SQL for postgres metadata: %s', self.sql_stmt)

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
        for _, group in groupby(self._get_raw_extract_iter(), self._get_table_key):
            # columns is a list of ColumnMetadata values
            columns = []

            # each row in group represents a row in the returned SQL query.
            # you can adjust the query to bring in more information and access it
            # as a dictionary i.e row['some_new_column']
            for row in group:
                last_row = row

                column_badges = []
                # Example 1: Partition Column i.e par_region
                if 'par_' in row['col_name']:
                    column_badges.append('Partition Column')

                # Example 2: Let's say column description contains the sensitivity or PII information
                if 'sensitivitiy' in row['col_description'].casefold():
                    column_badges.append("Contains PII")

                # Example 3: Let's say this column is a business date key or equivalent
                if '_date' in row['col_name'] or '_time' in row['col_name']:
                    column_badges.append("Business Date Key")

                columns.append(
                    ColumnMetadata(
                        name=row['col_name'],
                        description=row['col_description'],
                        col_type=row['col_type'],
                        sort_order=row['col_sort_order'],
                        badges=column_badges
                    )
                )

            # set up table tags and badges
            table_badges = [] # will be title-cased in the front end
            table_tags = [] # must be _ seperated
            # Example 1: Grab the table type i.e EXTERNAL, PHYSICAL, or VIEW assuming you bring this info in
            if last_row['table_type']:
                table_badges.append(last_row['table_type'])
                # i.e "PHYSICAL TABLE" -> "physical_table" for the tag
                table_tags.append(last_row['table_type'].replace(" ", "_"))

            # new feature: set up programmatic descriptions to appear
            programmatic_descs = {
                "Table Information": "Insert some description here that can be derived from a column",
                "Example Desc": f"This object is a {last_row['table_type']}.", # i.e "this object is a view"
                "Example Desc 2": "To ask questions about this table, please reach out to "
                                  "[some_support_url](insert_some_url_here)"
            }

            yield TableMetadata(
                database=self._database, # the database that the metadata comes from -> postgres
                cluster=last_row['cluster'], # the database that the data comes from
                schema=last_row['schema'],
                name=last_row['name'],
                columns=columns,
                # The default `description_source` is "description" which is the Amundsen UI description field.
                # The programmatic ones added as non-editable heading/texts in the UI.
                description=last_row['description'],
                tags=table_tags,
                badges=table_badges,
                programmatic_descriptions=programmatic_descs
            )

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
