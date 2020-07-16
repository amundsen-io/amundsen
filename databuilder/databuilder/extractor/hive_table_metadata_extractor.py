# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from collections import namedtuple

from pyhocon import ConfigFactory, ConfigTree  # noqa: F401
from typing import Iterator, Union, Dict, Any  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata
from itertools import groupby


TableKey = namedtuple('TableKey', ['schema', 'table_name'])

LOGGER = logging.getLogger(__name__)


class HiveTableMetadataExtractor(Extractor):
    """
    Extracts Hive table and column metadata from underlying meta store database using SQLAlchemyExtractor
    """
    # SELECT statement from hive metastore database to extract table and column metadata
    # Below SELECT statement uses UNION to combining two queries together.
    # 1st query is retrieving partition columns
    # 2nd query is retrieving columns
    # Using UNION to combine above two statements and order by table & partition identifier.
    SQL_STATEMENT = """
    SELECT source.* FROM
    (SELECT t.TBL_ID, d.NAME as `schema`, t.TBL_NAME name, t.TBL_TYPE, tp.PARAM_VALUE as description,
           p.PKEY_NAME as col_name, p.INTEGER_IDX as col_sort_order,
           p.PKEY_TYPE as col_type, p.PKEY_COMMENT as col_description, 1 as "is_partition_col",
           IF(t.TBL_TYPE = 'VIRTUAL_VIEW', 1, 0) "is_view"
    FROM TBLS t
    JOIN DBS d ON t.DB_ID = d.DB_ID
    JOIN PARTITION_KEYS p ON t.TBL_ID = p.TBL_ID
    LEFT JOIN TABLE_PARAMS tp ON (t.TBL_ID = tp.TBL_ID AND tp.PARAM_KEY='comment')
    {where_clause_suffix}
    UNION
    SELECT t.TBL_ID, d.NAME as `schema`, t.TBL_NAME name, t.TBL_TYPE, tp.PARAM_VALUE as description,
           c.COLUMN_NAME as col_name, c.INTEGER_IDX as col_sort_order,
           c.TYPE_NAME as col_type, c.COMMENT as col_description, 0 as "is_partition_col",
           IF(t.TBL_TYPE = 'VIRTUAL_VIEW', 1, 0) "is_view"
    FROM TBLS t
    JOIN DBS d ON t.DB_ID = d.DB_ID
    JOIN SDS s ON t.SD_ID = s.SD_ID
    JOIN COLUMNS_V2 c ON s.CD_ID = c.CD_ID
    LEFT JOIN TABLE_PARAMS tp ON (t.TBL_ID = tp.TBL_ID AND tp.PARAM_KEY='comment')
    {where_clause_suffix}
    ) source
    ORDER by tbl_id, is_partition_col desc;
    """

    # CONFIG KEYS
    WHERE_CLAUSE_SUFFIX_KEY = 'where_clause_suffix'
    CLUSTER_KEY = 'cluster'

    DEFAULT_CONFIG = ConfigFactory.from_dict({WHERE_CLAUSE_SUFFIX_KEY: ' ',
                                              CLUSTER_KEY: 'gold'})

    def init(self, conf):
        # type: (ConfigTree) -> None
        conf = conf.with_fallback(HiveTableMetadataExtractor.DEFAULT_CONFIG)
        self._cluster = '{}'.format(conf.get_string(HiveTableMetadataExtractor.CLUSTER_KEY))

        self.sql_stmt = HiveTableMetadataExtractor.SQL_STATEMENT.format(
            where_clause_suffix=conf.get_string(HiveTableMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY))

        LOGGER.info('SQL for hive metastore: {}'.format(self.sql_stmt))

        self._alchemy_extractor = SQLAlchemyExtractor()
        sql_alch_conf = Scoped.get_scoped_conf(conf, self._alchemy_extractor.get_scope())\
            .with_fallback(ConfigFactory.from_dict({SQLAlchemyExtractor.EXTRACT_SQL: self.sql_stmt}))

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
        return 'extractor.hive_table_metadata'

    def _get_extract_iter(self):
        # type: () -> Iterator[TableMetadata]
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
            is_view = last_row['is_view'] == 1
            yield TableMetadata('hive', self._cluster,
                                last_row['schema'],
                                last_row['name'],
                                last_row['description'],
                                columns,
                                is_view=is_view)

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
            return TableKey(schema=row['schema'], table_name=row['name'])

        return None
