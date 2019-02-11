import logging
from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker
from typing import Iterable, List  # noqa: F401

from databuilder.sql_parser.usage.column import Column, Table, remove_double_quotes
from databuilder.sql_parser.usage.presto.antlr_generated.SqlBaseLexer import SqlBaseLexer
from databuilder.sql_parser.usage.presto.antlr_generated.SqlBaseListener import SqlBaseListener
from databuilder.sql_parser.usage.presto.antlr_generated.SqlBaseParser import SqlBaseParser


LOGGER = logging.getLogger(__name__)


class ColumnUsageListener(SqlBaseListener):
    """
    ColumnUsageListener that inherits Antlr generated SqlBaseListener so that it can extract column and table usage
    while ColumnUsageListener walks the parsing tree.

    (Method name is from Antlr generated SqlBaseListener where it does not follow python convention)

    Basic idea of column extraction is to look at SELECT statement as two parts.
     1. processing columns: Columns in SELECT clause. (SELECT foo, bar )
     2. processed columns: Columns in FROM clause. (FROM foobar or FROM (SELECT foo, bar from foobar) )

    Overall, we'd like to retrieve processing column. Thus, the problem we need to solve is basically based on
    processed column, finalize processing column by get the necessary info (such as table, schema) from processed
    column.
    """
    def __init__(self):
        # type: () -> None
        self.processed_cols = []  # type: List[Column]
        self._processing_cols = []  # type: List[Column]
        self._current_col = None  # type: Column
        self._stack = []  # type: List[Column]

    def exitColumnReference(self,
                            ctx  # type: SqlBaseParser.ColumnReferenceContext
                            ):
        # type: (...) -> None

        """
        Call back method for column that does not have table indicator
        :param ctx:
        :return:
        """
        self._current_col = Column(ctx.getText())

    def exitDereference(self,
                        ctx  # type: SqlBaseParser.DereferenceContext
                        ):
        # type: (...) -> None
        """
        Call back method for column with table indicator e.g: foo.bar
        :param ctx:
        :return:
        """
        self._current_col = Column(ctx.identifier().getText(),
                                   table=Table(ctx.base.getText()))

    def exitSelectSingle(self,
                         ctx  # type: SqlBaseParser.SelectSingleContext
                         ):
        # type: (...) -> None
        """
        Call back method for select single column. This is to distinguish
        between columns for SELECT statement and columns for something else
        such as JOIN statement
        :param ctx:
        :return:
        """
        if not self._current_col:
            return

        if ctx.identifier():
            self._current_col.col_alias = remove_double_quotes(ctx.identifier().getText())

        self._processing_cols.append(self._current_col)
        self._current_col = None

    def exitSelectAll(self,
                      ctx  # type: SqlBaseParser.SelectAllContext
                      ):
        # type: (...) -> None
        """
        Call back method for select ALL column.
        :param ctx:
        :return:
        """
        self._current_col = Column('*')
        if ctx.qualifiedName():
            self._current_col.table = Table(ctx.qualifiedName().getText())

        self._processing_cols.append(self._current_col)
        self._current_col = None

    def exitTableName(self,
                      ctx  # type: SqlBaseParser.TableNameContext
                      ):
        # type: (...) -> None
        """
        Call back method for table name
        :param ctx:
        :return:
        """
        table_name = ctx.getText()
        table = Table(table_name)
        if '.' in table_name:
            db_tbl = table_name.split('.')
            table = Table(db_tbl[len(db_tbl) - 1],
                          schema=db_tbl[len(db_tbl) - 2])

        self._current_col = Column('*', table=table)

    def exitAliasedRelation(self,
                            ctx  # type: SqlBaseParser.AliasedRelationContext
                            ):
        # type: (...) -> None
        """
        Call back method for table alias
        :param ctx:
        :return:
        """
        if not ctx.identifier():
            return

        # Table alias for column
        if self._current_col and self._current_col.table:
            self._current_col.table.alias = remove_double_quotes(ctx.identifier().getText())
            return

        # Table alias for inner SQL
        for col in self.processed_cols:
            col.table.alias = remove_double_quotes(ctx.identifier().getText())

    def exitRelationDefault(self,
                            ctx  # type: SqlBaseParser.RelationDefaultContext
                            ):
        # type: (...) -> None
        """
        Callback method when exiting FROM clause. Here we are moving processing columns to processed
        to processed
        :param ctx:
        :return:
        """
        if not self._current_col:
            return

        self.processed_cols.append(self._current_col)
        self._current_col = None

    def enterQuerySpecification(self,
                                ctx  # type: SqlBaseParser.QuerySpecificationContext
                                ):
        # type: (...) -> None
        """
        Callback method for Query specification. For nested SELECT
        statement, it will store previous processing column to stack.
        :param ctx:
        :return:
        """
        if not self._processing_cols:
            return

        self._stack.append(self._processing_cols)
        self._processing_cols = []

    def exitQuerySpecification(self,
                               ctx  # type: SqlBaseParser.QuerySpecificationContext
                               ):
        # type: (...) -> None
        """
        Call back method for Query specification. It merges processing
        columns with processed column
        :param ctx:
        :return:
        """

        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug('processing_cols: {}'.format(self._processing_cols))
            LOGGER.debug('processed_cols: {}'.format(self.processed_cols))

        result = []

        for col in self._processing_cols:
            for resolved in Column.resolve(col, self.processed_cols):
                result.append(resolved)

        self.processed_cols = result
        self._processing_cols = []
        if self._stack:
            self._processing_cols = self._stack.pop()

        self._current_col = None

        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug('done processing_cols: {}'.format(self._processing_cols))
            LOGGER.debug('done processed_cols: {}'.format(self.processed_cols))


class ColumnUsageProvider(object):
    def __init__(self):
        # type: () -> None
        pass

    @classmethod
    def get_columns(cls, query):
        # type: (str) -> Iterable[Column]
        """
        Using presto Grammar, instantiate Parsetree, attach ColumnUsageListener to tree and walk the tree.
        Once finished walking the tree, listener will have selected columns and return them.
        :param query:
        :return:
        """

        query = query.rstrip(';').upper() + "\n"
        lexer = SqlBaseLexer(InputStream(query))
        parser = SqlBaseParser(CommonTokenStream(lexer))
        parse_tree = parser.singleStatement()

        listener = ColumnUsageListener()
        walker = ParseTreeWalker()
        walker.walk(listener, parse_tree)

        return listener.processed_cols
