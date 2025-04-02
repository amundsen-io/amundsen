# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from typing import (  # noqa: F401
    Any, Dict, Iterator, Union,
)

from pyhocon import ConfigFactory, ConfigTree  # noqa: F401

from databuilder.extractor.base_postgres_metadata_extractor import BasePostgresMetadataExtractor
from databuilder.models.table_last_updated import TableLastUpdated
from datetime import datetime

LOGGER = logging.getLogger(__name__)

class RedshiftTableLastUpdatedExtractor(BasePostgresMetadataExtractor):
    """
    Extracts Redshift table last update information from underlying meta store database using SQLAlchemyExtractor
    """

    def get_sql_statement(self, use_catalog_as_cluster_name: bool, where_clause_suffix: str) -> str:
        if use_catalog_as_cluster_name:
            cluster_source = "CURRENT_DATABASE()"
        else:
            cluster_source = f"'{self._cluster}'"

        return """
        SELECT
            {cluster_source} AS cluster,
            sti.database AS database,
            sti.schema AS schema,
            sti.table AS table_name,
            MAX(inserts.endtime) AS last_updated_time
        FROM stl_insert AS inserts
        JOIN svv_table_info AS sti ON sti.table_id = inserts.tbl
        {where_clause_suffix}
        GROUP BY cluster, database, schema, table_name
        ORDER by cluster, database, schema, table_name ;
        """.format(
            cluster_source=cluster_source,
            where_clause_suffix=where_clause_suffix,
        )

    def extract(self) -> Union[TableLastUpdated, None]:
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)

        except StopIteration:
            return None

    def get_scope(self) -> str:
        return 'extractor.redshift_table_last_updated'

    def _get_extract_iter(self) -> Iterator[TableLastUpdated]:
        """
        Provides iterator of result row from SQLAlchemy extractor
        """
        tbl_last_updated_row = self._alchemy_extractor.extract()
        while tbl_last_updated_row:
            yield TableLastUpdated(table_name=tbl_last_updated_row['table_name'],
                                   last_updated_time_epoch=datetime.timestamp(tbl_last_updated_row['last_updated_time']),
                                   schema=tbl_last_updated_row['schema'],
                                   db=self._database,
                                   cluster=tbl_last_updated_row['cluster'])
            tbl_last_updated_row = self._alchemy_extractor.extract()
