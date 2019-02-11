
import copy
import logging

import six
from typing import Union, Iterable, Optional  # noqa: F401

LOGGER = logging.getLogger(__name__)


def remove_double_quotes(val):
    # type: (Union[str, None]) -> Union[str, None]
    """
    Often times, column name, table name or any identifier comes with double quoted. This method will remove double
    quotes.
    :param val:
    :return:
    """
    if not val:
        return val

    if six.PY2 and isinstance(val, six.text_type):
        val = val.encode('utf-8', 'ignore')

    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    return val


class Column(object):
    """
    Column for usage.
    """
    def __init__(self, name, table=None, col_alias=None):
        # type: (str, Union[Table, None], Union[str, None]) -> None
        self.col_name = remove_double_quotes(name)
        self.table = table
        self.col_alias = remove_double_quotes(col_alias)

    def __repr__(self):
        # type: () -> str
        return 'Column(name={!r}, table={!r}, col_alias={!r})'.format(self.col_name, self.table, self.col_alias)

    def resolve_col_name(self, col_name):
        # type: (Union[str, None]) -> Union[str, None]
        """
        Resolve column name for currently processing column.
        e.g: SELECT bar from (SELECT foo as bar FROM foobar)
        Above case, bar is trying to resolve with column foo that has alias bar. In this case, it will resolve to foo,
        as that is the actual column name.
        :param col_name:
        :return:
        """
        if self.col_name == '*':
            return col_name

        if col_name == self.col_alias or col_name == self.col_name:
            return self.col_name

        return None

    @staticmethod
    def resolve(select_col, from_cols):
        # type: (Column, Iterable[Column]) -> Iterable[Column]
        """
        Resolve processing column with processed columns. Processing column is the one from SELECT clause where it
        does not have table information where it can optionally have table alias in front of column (foo.bar)
        Processed columns are already resolved columns that it has column with table with it.

        Resolving processing columns with processed columns means having processing columns choose correct processed
        columns. The result is proper column name with table name.

        e.g1: SELECT foo from foobar
         - processing column: foo
         - processed column: all columns from foobar
         --> result: column 'foo' from 'foobar' table

        e.g2: SELECT foo from (SELECT foo, bar FROM foobar)
         - processing column: foo
         - processed column: foo and bar columns from foobar
         --> result: column 'foo' from 'foobar' table

        :param select_col: column from select clause
        :param from_cols: column from 'from' clause
        :return: List of columns
        """
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug('select_col: {}'.format(select_col))
            LOGGER.debug('from_cols: {}'.format(from_cols))

        if select_col.col_name != '*':
            return Column.resolve_named_column(select_col, from_cols)

        return Column._resolve_all_column(select_col, from_cols)

    @staticmethod
    def resolve_named_column(select_col, from_cols):
        # type: (Column, Iterable[Column]) -> Iterable[Column]
        """
        SELECT clause where column has name (not *)
        e.g: SELECT foo, bar FROM foobar.

        :param select_col: column from select clause
        :param from_cols: column from 'from' clause
        :return:
        """
        # column name is defined and has table alias. (SELECT foo.bar)
        if select_col.table:
            for processed_col in from_cols:
                # resolve column name as processing column name can be alias
                col_name = processed_col.resolve_col_name(select_col.col_name)
                if col_name and processed_col.table:
                    # resolve table name using alias
                    table = processed_col.table.resolve_table(select_col.table.name)
                    if table:
                        alias = Column.get_column_alias(select_col=select_col, from_col=processed_col)
                        col = Column(col_name, table=table, col_alias=alias)
                        return [col]
            raise Exception('Cannot found case 1. select_col: {} , from_cols: {}'
                            .format(select_col, from_cols))
        # col name defined but no table. (SELECT foo)
        else:
            sub_result = []
            # Using column name only to find a match from processed column.
            # Note that we can have a column name with multiple table as a result. This is the case that SQL engine
            # resolves ambiguity by looking into actual columns in table. Here we use OrTable so that later on it
            #  can be disambiguated.
            for processed_col in from_cols:
                col_name = processed_col.resolve_col_name(select_col.col_name)
                if col_name:
                    col = copy.deepcopy(processed_col)
                    col.col_name = col_name
                    alias = Column.get_column_alias(select_col=select_col, from_col=processed_col)
                    col.col_alias = alias
                    sub_result.append(col)

            if not sub_result:
                raise Exception('Cannot find case 2. select_col: {} , from_cols: {}'
                                .format(select_col, from_cols))
            if len(sub_result) == 1:
                return sub_result

            tables = []
            for col in sub_result:
                tables.append(copy.deepcopy(col.table))
            col = sub_result[0]
            col.table = OrTable(tables)
            return [col]

    @staticmethod
    def get_column_alias(select_col, from_col):
        # type: (Column, Column) -> str
        """
        Use processing column alias if not null.
        :param select_col: column from select clause
        :param from_col: column from 'from' clause
        :return:
        """
        return select_col.col_alias if select_col.col_alias else from_col.col_alias

    @staticmethod
    def _resolve_all_column(processing_col, processed_cols):
        # type: (Column, Iterable[Column]) -> Iterable[Column]
        """
        SELECT statement where column is '*'
        e.g: SELECT * FROM foobar;
        :param processed_cols:
        :return:
        """
        if processing_col.table:
            result = []
            # Select whatever we have in processed where it just need to match table
            for processed_col in processed_cols:
                if processed_col.table:
                    table = processed_col.table.resolve_table(processing_col.table.name)
                if table:
                    col = copy.deepcopy(processed_col)
                    col.table = table
                    result.append(col)
            if not result:
                raise Exception('Cannot find case 3. select_col: {} , from_cols: {}'
                                .format(processing_col, processed_cols))
            return result

        # SELECT * case
        else:
            result = []
            for processed_col in processed_cols:
                result.append(copy.deepcopy(processed_col))
            if not result:
                raise Exception('Cannot find case 4. select_col: {} , from_cols: {}'
                                .format(processing_col, processed_cols))
            return result


class Table(object):
    """
    Table class for usage
    """
    def __init__(self, name, schema=None, alias=None):
        # type: (str, Union[str, None], Union[str, None]) -> None
        self.name = remove_double_quotes(name)
        self.schema = remove_double_quotes(schema)
        self.alias = remove_double_quotes(alias)

    def resolve_table(self, select_table_name):
        # type: (Union[str, None]) -> Union[Table, None]
        """
        If processing_table_name matches table return table instance
        :param select_table_name: table in select clause
        :return:
        """
        if select_table_name == self.alias or select_table_name == self.name:
            return self
        return None

    def __repr__(self):
        # type: () -> str
        return 'Table(name={!r}, schema={!r}, alias={!r})'.format(self.name, self.schema, self.alias)


class OrTable(Table):
    """
    Table that holds multiple table. This is for ambiguous case.
    For example, "SELECT a, b FROM foo JOIN bar USING c" statement does not tell if column a is from foo or bar.
    Thus, column a is either from table foo or bar and this class represent this problem.
    """
    def __init__(self, tables):
        # type: (Iterable[Optional[Table]]) -> None
        self.tables = tables

    def resolve_table(self, select_table_name):
        # type: (str) -> Optional[Table]
        """
        If any of term matches with table return it
        :param select_table_name:
        :return:
        """
        for table in self.tables:
            if isinstance(table, OrTable):
                result = table.resolve_table(select_table_name)
                if result:
                    return result
                continue

            if select_table_name == table.alias or select_table_name == table.name:
                return table
        return None

    def __repr__(self):
        # type: () -> str
        return 'OrTable(tables={!r})'.format(self.tables)
