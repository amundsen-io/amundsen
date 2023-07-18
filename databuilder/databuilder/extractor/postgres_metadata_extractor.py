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
            cluster_source = "current_database()"
        else:
            cluster_source = f"'{self._cluster}'"

        return """
             SELECT DISTINCT
 {cluster_source} as cluster,
 svc.table_schema as schema,
 svc.table_name as name,
 tnd.description as description,
 svc.column_name as col_name,
 svc.data_type as col_type,
svec.part_key as  "is_partition_col",
 tncd.description as col_description ,
 svc.ordinal_position as col_sort_order
 FROM pg_catalog.svv_columns as svc
 LEFT JOIN
  public.amundsen_table_new_descrption  tnd
   on tnd.name = svc.table_name and  tnd.schemaname=svc.table_schema
 LEFT JOIN
               public.amundsen_table_new_col_desc tncd
               on tncd.tablename= svc.table_name and tncd.colname= svc.column_name and tncd.schemaname = svc.table_schema
LEFT JOIN
   pg_catalog.svv_tables svt
on svt.table_name = svc.table_name and svt.table_schema = svc.table_schema
LEFT JOIN
   pg_catalog.svv_external_columns svec
 on  svec.tablename = svc.table_name  and  svec.columnname = svc.column_name and  svec.schemaname=  svc.table_schema
 where {where_clause_suffix}
 ORDER by cluster, schema, name, col_sort_order


        """.format(
            cluster_source=cluster_source,
            where_clause_suffix=where_clause_suffix,
        )

    def get_scope(self) -> str:
        return 'extractor.postgres_metadata'