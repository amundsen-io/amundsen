# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (  # noqa: F401
    Any, Dict, Iterator, Union,
)

from pyhocon import ConfigFactory, ConfigTree  # noqa: F401

from databuilder.extractor.base_postgres_metadata_extractor import BasePostgresMetadataExtractor


class PostgresMetadataExtractor(BasePostgresMetadataExtractor):
    """
    Extracts Postgres table and column metadata from underlying meta store database using SQLAlchemyExtractor
    """

    def get_sql_statement(self, use_catalog_as_cluster_name: bool, where_clause_suffix: str) -> str:
        if use_catalog_as_cluster_name:
            cluster_source = "c.table_catalog"
        else:
            cluster_source = f"'{self._cluster}'"

        return """
        SELECT
          {cluster_source} as cluster, c.table_schema as schema, c.table_name as name, pgtd.description as description
          ,c.column_name as col_name, c.data_type as col_type
          , pgcd.description as col_description, ordinal_position as col_sort_order
        FROM INFORMATION_SCHEMA.COLUMNS c
        INNER JOIN
          pg_catalog.pg_statio_all_tables as st on c.table_schema=st.schemaname and c.table_name=st.relname
        LEFT JOIN
          pg_catalog.pg_description pgcd on pgcd.objoid=st.relid and pgcd.objsubid=c.ordinal_position
        LEFT JOIN
          pg_catalog.pg_description pgtd on pgtd.objoid=st.relid and pgtd.objsubid=0
        {where_clause_suffix}
        ORDER by cluster, schema, name, col_sort_order ;
        """.format(
            cluster_source=cluster_source,
            where_clause_suffix=where_clause_suffix,
        )

    def get_scope(self) -> str:
        return 'extractor.postgres_metadata'
