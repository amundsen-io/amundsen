# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import base64
import json
import logging

from pyhocon import ConfigFactory, ConfigTree  # noqa: F401
from typing import Iterator, Union, Dict, Any  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata


LOGGER = logging.getLogger(__name__)


class PrestoViewMetadataExtractor(Extractor):
    """
    Extracts Presto View and column metadata from underlying meta store database using SQLAlchemyExtractor
    PrestoViewMetadataExtractor does not require a separate table model but just reuse the existing TableMetadata
    """
    # SQL statement to extract View metadata
    # {where_clause_suffix} could be used to filter schemas
    SQL_STATEMENT = """
    SELECT t.TBL_ID, d.NAME as `schema`, t.TBL_NAME name, t.TBL_TYPE, t.VIEW_ORIGINAL_TEXT as view_original_text
    FROM TBLS t
    JOIN DBS d ON t.DB_ID = d.DB_ID
    WHERE t.VIEW_EXPANDED_TEXT = '/* Presto View */'
    {where_clause_suffix}
    ORDER BY t.TBL_ID desc;
    """

    # Presto View data prefix and suffix definition:
    # https://github.com/prestodb/presto/blob/43bd519052ba4c56ff1f4fc807075637ab5f4f10/presto-hive/src/main/java/com/facebook/presto/hive/HiveUtil.java#L153-L154
    PRESTO_VIEW_PREFIX = '/* Presto View: '
    PRESTO_VIEW_SUFFIX = ' */'

    # CONFIG KEYS
    WHERE_CLAUSE_SUFFIX_KEY = 'where_clause_suffix'
    CLUSTER_KEY = 'cluster'

    DEFAULT_CONFIG = ConfigFactory.from_dict({WHERE_CLAUSE_SUFFIX_KEY: ' ',
                                              CLUSTER_KEY: 'gold'})

    def init(self, conf):
        # type: (ConfigTree) -> None
        conf = conf.with_fallback(PrestoViewMetadataExtractor.DEFAULT_CONFIG)
        self._cluster = '{}'.format(conf.get_string(PrestoViewMetadataExtractor.CLUSTER_KEY))

        self.sql_stmt = PrestoViewMetadataExtractor.SQL_STATEMENT.format(
            where_clause_suffix=conf.get_string(PrestoViewMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY))

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
        return 'extractor.presto_view_metadata'

    def _get_extract_iter(self):
        # type: () -> Iterator[TableMetadata]
        """
        Using itertools.groupby and raw level iterator, it groups to table and yields TableMetadata
        :return:
        """
        row = self._alchemy_extractor.extract()
        while row:
            columns = self._get_column_metadata(row['view_original_text'])
            yield TableMetadata(database='presto',
                                cluster=self._cluster,
                                schema=row['schema'],
                                name=row['name'],
                                description=None,
                                columns=columns,
                                is_view=True)
            row = self._alchemy_extractor.extract()

    def _get_column_metadata(self, view_original_text):
        # type: (str) -> List[ColumnMetadata]
        """
        Get Column Metadata from VIEW_ORIGINAL_TEXT from TBLS table for Presto Views.
        Columns are sorted the same way as they appear in Presto Create View SQL.
        :param view_original_text:
        :return:
        """
        # remove encoded Presto View data prefix and suffix
        encoded_view_info = (
            view_original_text.
            split(PrestoViewMetadataExtractor.PRESTO_VIEW_PREFIX, 1)[-1].
            rsplit(PrestoViewMetadataExtractor.PRESTO_VIEW_SUFFIX, 1)[0]
        )

        # view_original_text is b64 encoded:
        # https://github.com/prestodb/presto/blob/43bd519052ba4c56ff1f4fc807075637ab5f4f10/presto-hive/src/main/java/com/facebook/presto/hive/HiveUtil.java#L602-L605
        decoded_view_info = base64.b64decode(encoded_view_info)
        columns = json.loads(decoded_view_info).get('columns')

        return [ColumnMetadata(name=column['name'],
                               description=None,
                               col_type=column['type'],
                               sort_order=i) for i, column in enumerate(columns)]
