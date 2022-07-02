# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (  # noqa: F401
    Any, Dict, Iterator, Union,
)

from pyhocon import ConfigFactory, ConfigTree  # noqa: F401

from databuilder.extractor.base_teradata_metadata_extractor import BaseTeradataMetadataExtractor


class TeradataMetadataExtractor(BaseTeradataMetadataExtractor):
    """
    Extracts Teradata table and column metadata from underlying meta store database using SQLAlchemyExtractor
    """

    def get_sql_statement(
        self, use_catalog_as_cluster_name: bool, where_clause_suffix: str
    ) -> str:
        if use_catalog_as_cluster_name:
            cluster_source = "current_database()"
        else:
            cluster_source = f"'{self._cluster}'"

        return """
            SELECT
                {cluster_source} as td_cluster,
                c.DatabaseName as schema,
                c.TableName as name,
                c.CommentString as description,
                d.ColumnName as col_name,
                d.ColumnType as col_type,
                d.CommentString as col_description,
                d.ColumnId as col_sort_order
            FROM dbc.Tables c, dbc.Columns d
            WHERE c.DatabaseName = d.DatabaseName AND c.TableName = d.TableName
            AND {where_clause_suffix}
            ORDER by cluster_a, schema, name, col_sort_order;
        """.format(
            cluster_source=cluster_source,
            where_clause_suffix=where_clause_suffix,
        )

    def get_scope(self) -> str:
        return "extractor.teradata_metadata"
