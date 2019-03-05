from collections import namedtuple
import logging

from pyhocon import ConfigTree  # noqa: F401
from typing import Dict, List, Any, Optional  # noqa: F401

from databuilder import Scoped
from databuilder.transformer.base_transformer import NoopTransformer
from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_column_usage import ColumnReader, TableColumnUsage
from databuilder.transformer.base_transformer import ChainedTransformer
from databuilder.transformer.regex_str_replace_transformer import RegexStrReplaceTransformer
from databuilder.transformer.sql_to_table_col_usage_transformer import SqlToTblColUsageTransformer

TableColumnUsageTuple = namedtuple('TableColumnUsageTuple', ['database', 'cluster', 'schema',
                                                             'table', 'column', 'email'])

LOGGER = logging.getLogger(__name__)


# Config keys:
RAW_EXTRACTOR = 'raw_extractor'


class TblColUsgAggExtractor(Extractor):
    """
    An aggregate extractor for table column usage.
    It uses RegexStrReplaceTransformer to cleanse SQL statement and uses SqlToTblColUsageTransformer to get table
    column usage.

    All usage will be aggregated in memory and on last record, it will return aggregated TableColumnUsage
    Note that this extractor will do all the transformation and aggregation so that no more transformation is needed,
    after this.
    """

    def init(self, conf):
        # type: (ConfigTree) -> None
        self._extractor = conf.get(RAW_EXTRACTOR)  # type: Extractor
        self._extractor.init(Scoped.get_scoped_conf(conf, self._extractor.get_scope()))

        regex_transformer = RegexStrReplaceTransformer()  # type: Any
        if conf.get(regex_transformer.get_scope(), None):
            regex_transformer.init(Scoped.get_scoped_conf(conf, regex_transformer.get_scope()))
        else:
            LOGGER.info('{} is not defined. Not using it'.format(regex_transformer.get_scope()))
            regex_transformer = NoopTransformer()

        sql_to_usage_transformer = SqlToTblColUsageTransformer()
        sql_to_usage_transformer.init(Scoped.get_scoped_conf(conf, sql_to_usage_transformer.get_scope()))

        self._transformer = ChainedTransformer((regex_transformer, sql_to_usage_transformer))

    def extract(self):
        # type: () -> Optional[TableColumnUsage]
        """
        It aggregates all count per table and user in memory. Table level aggregation don't expect to occupy much
        memory.
        :return: Provides a record or None if no more to extract
        """
        count_map = {}  # type: Dict[TableColumnUsageTuple, int]
        record = self._extractor.extract()

        count = 0
        while record:
            count += 1
            if count % 1000 == 0:
                LOGGER.info('Aggregated {} records'.format(count))

            tbl_col_usg = self._transformer.transform(record=record)
            record = self._extractor.extract()
            # filtered case
            if not tbl_col_usg:
                continue

            for col_rdr in tbl_col_usg.col_readers:
                key = TableColumnUsageTuple(database=col_rdr.database, cluster=col_rdr.cluster, schema=col_rdr.schema,
                                            table=col_rdr.table, column=col_rdr.column, email=col_rdr.user_email)
                new_count = count_map.get(key, 0) + col_rdr.read_count
                count_map[key] = new_count

        if not len(count_map):
            return None

        col_readers = []  # type: List[ColumnReader]

        while len(count_map):
            tbl_col_rdr_tuple, count = count_map.popitem()
            col_readers.append(ColumnReader(database=tbl_col_rdr_tuple.database, cluster=tbl_col_rdr_tuple.cluster,
                                            schema=tbl_col_rdr_tuple.schema, table=tbl_col_rdr_tuple.table,
                                            column=tbl_col_rdr_tuple.column, user_email=tbl_col_rdr_tuple.email,
                                            read_count=count))

        return TableColumnUsage(col_readers=col_readers)

    def get_scope(self):
        # type: () -> str
        return 'extractor.table_column_usage_aggregate'

    def close(self):
        # type: () -> None
        self._transformer.close()
