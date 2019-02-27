import logging
from multiprocessing.pool import ThreadPool, TimeoutError

from pyhocon import ConfigTree  # noqa: F401
from typing import Any, Optional, List, Iterable  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.hive_table_metadata_extractor import HiveTableMetadataExtractor
from databuilder.models.table_column_usage import TableColumnUsage, ColumnReader
from databuilder.sql_parser.usage.column import OrTable, Table  # noqa: F401
from databuilder.sql_parser.usage.presto.column_usage_provider import ColumnUsageProvider
from databuilder.transformer.base_transformer import Transformer

LOGGER = logging.getLogger(__name__)


class SqlToTblColUsageTransformer(Transformer):
    """
    Note that it currently only supports Presto SQL.
    A SQL to usage transformer where it transforms to ColumnReader that has column, user, count.
    Currently it's collects on table level that column on same table will be de-duped.
    In many cases, "from" clause does not contain schema and this will be fetched via table name -> schema name mapping
    which it gets from Hive metastore. (Naming collision is disregarded as it needs column level to disambiguate)

    Currently, ColumnUsageProvider could hang on certain SQL statement and as a short term solution it will timeout
    processing statement at 10 seconds.
    """
    # Config key
    DATABASE_NAME = 'database'
    CLUSTER_NAME = 'cluster'
    SQL_STATEMENT_ATTRIBUTE_NAME = 'sql_stmt_attribute_name'
    USER_EMAIL_ATTRIBUTE_NAME = 'user_email_attribute_name'
    COLUMN_EXTRACTION_TIMEOUT_SEC = 'column_extraction_timeout_seconds'
    LOG_ALL_EXTRACTION_FAILURES = 'log_all_extraction_failures'

    total_counts = 0
    failure_counts = 0

    def init(self, conf):
        # type: (ConfigTree) -> None
        self._conf = conf
        self._database = conf.get_string(SqlToTblColUsageTransformer.DATABASE_NAME)
        self._cluster = conf.get_string(SqlToTblColUsageTransformer.CLUSTER_NAME, 'gold')
        self._sql_stmt_attr = conf.get_string(SqlToTblColUsageTransformer.SQL_STATEMENT_ATTRIBUTE_NAME)
        self._user_email_attr = conf.get_string(SqlToTblColUsageTransformer.USER_EMAIL_ATTRIBUTE_NAME)
        self._tbl_to_schema_mapping = self._create_schema_by_table_mapping()
        self._worker_pool = ThreadPool(processes=1)
        self._time_out_sec = conf.get_int(SqlToTblColUsageTransformer.COLUMN_EXTRACTION_TIMEOUT_SEC, 10)
        LOGGER.info('Column extraction timeout: {} seconds'.format(self._time_out_sec))
        self._log_all_extraction_failures = conf.get_bool(SqlToTblColUsageTransformer.LOG_ALL_EXTRACTION_FAILURES,
                                                          False)

    def transform(self, record):
        # type: (Any) -> Optional[TableColumnUsage]
        SqlToTblColUsageTransformer.total_counts += 1

        stmt = getattr(record, self._sql_stmt_attr)
        email = getattr(record, self._user_email_attr)

        result = []  # type: List[ColumnReader]
        try:
            columns = self._worker_pool.apply_async(ColumnUsageProvider.get_columns, (stmt,)).get(self._time_out_sec)
            # LOGGER.info('Statement: {} ---> columns: {}'.format(stmt, columns))
        except TimeoutError:
            SqlToTblColUsageTransformer.failure_counts += 1
            LOGGER.exception('Timed out while getting column usage from query: {}'.format(stmt))
            LOGGER.info('Killing the thread.')
            self._worker_pool.terminate()
            self._worker_pool = ThreadPool(processes=1)
            LOGGER.info('Killed the thread.')
            return None
        except Exception:
            SqlToTblColUsageTransformer.failure_counts += 1
            if self._log_all_extraction_failures:
                LOGGER.exception('Failed to get column usage from query: {}'.format(stmt))
            return None

        # Dedupe is needed to make it table level. TODO: Remove this once we are at column level
        dedupe_tuples = set()  # type: set
        for col in columns:
            sub_result = self._get_col_readers(table=col.table,
                                               stmt=stmt,
                                               email=email,
                                               dedupe_tuples=dedupe_tuples)
            result.extend(sub_result)

        if not result:
            return None

        return TableColumnUsage(col_readers=result)

    def _get_col_readers(self,
                         table,  # type: Table
                         stmt,  # type: str
                         email,  # type: str
                         dedupe_tuples  # type: set
                         ):
        # type: (...) -> Iterable[ColumnReader]
        """
        Using table information, produce column reader with de-duping same table as it's from same statement
        :param table:
        :param stmt:
        :param email:
        :param dedupe_tuples:
        :return:
        """

        result = []  # type: List[ColumnReader]
        self._get_col_readers_helper(table=table,
                                     stmt=stmt,
                                     email=email,
                                     dedupe_tuples=dedupe_tuples,
                                     result=result)
        return result

    def _get_col_readers_helper(self,
                                table,  # type: Table
                                stmt,  # type: str
                                email,  # type: str
                                dedupe_tuples,  # type: set
                                result  # type: List[ColumnReader]
                                ):
        # type: (...) -> None
        if not table:
            logging.warn('table does not exist. statement: {}'.format(stmt))
            return

        if isinstance(table, OrTable):
            for table in table.tables:
                self._get_col_readers_helper(table=table,
                                             stmt=stmt,
                                             email=email,
                                             dedupe_tuples=dedupe_tuples,
                                             result=result)
            return

        if self._is_duplicate(table=table, email=email, dedupe_tuples=dedupe_tuples):
            return

        schema = self._get_schema(table)
        if not schema:
            return

        result.append(ColumnReader(database=self._database,
                                   cluster=self._cluster,
                                   schema=schema,
                                   table=table.name,
                                   column='*',
                                   user_email=email))

    def _is_duplicate(self, table, email, dedupe_tuples):
        # type: (Table, str, set) -> bool
        """
        This is to only produce table level usage. TODO: Remove this
        :param table:
        :param email:
        :param dedupe_tuples:
        :return:
        """
        dedupe_tuple = (self._database, self._get_schema(table), table.name, email)
        if dedupe_tuple in dedupe_tuples:
            return True

        dedupe_tuples.add(dedupe_tuple)
        return False

    def get_scope(self):
        # type: () -> str
        return 'transformer.sql_to_tbl_col_usage'

    def _create_schema_by_table_mapping(self):
        # type: () -> dict
        # TODO: Make extractor generic
        table_metadata_extractor = HiveTableMetadataExtractor()
        table_metadata_extractor.init(Scoped.get_scoped_conf(self._conf, table_metadata_extractor.get_scope()))

        table_to_schema = {}
        table_metadata = table_metadata_extractor.extract()
        while table_metadata:
            # TODO: deal with collision
            table_to_schema[table_metadata.name.lower()] = table_metadata.schema_name.lower()
            table_metadata = table_metadata_extractor.extract()
        return table_to_schema

    def _get_schema(self, table):
        # type: (Table) -> Optional[str]
        if table.schema:
            return table.schema.lower()

        return self._tbl_to_schema_mapping.get(table.name.lower())

    def close(self):
        # type: () -> None
        LOGGER.info('Column usage stats: failure: {fail_count} out of total {total_count}'
                    .format(fail_count=SqlToTblColUsageTransformer.failure_counts,
                            total_count=SqlToTblColUsageTransformer.total_counts))
