# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import csv
import importlib
from collections import defaultdict
from typing import Any, List

from pyhocon import ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.badge import Badge, BadgeMetadata
from databuilder.models.table_lineage import ColumnLineage, TableLineage
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from databuilder.models.query.query import QueryMetadata
from databuilder.models.query.query_join import QueryJoinMetadata
from databuilder.models.query.query_execution import QueryExecutionsMetadata
from databuilder.models.query.query_where import QueryWhereMetadata
from databuilder.models.user import User as UserMetadata

def split_badge_list(badges: str, separator: str) -> List[str]:
    """
    Splits a string of badges into a list, removing all empty badges.
    """
    if badges is None:
        return []

    return [badge for badge in badges.split(separator) if badge]

def split_table_list(tables: str, separator: str) -> List[str]:
    """
    Splits a string of tables into a list, removing all empty tables.
    """
    if tables is None:
        return []

    return [table for table in tables.split(separator) if table]


class CsvExtractor(Extractor):
    # Config keys
    FILE_LOCATION = 'file_location'

    """
    An Extractor that extracts records via CSV.
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
        self.file_location = conf.get_string(CsvExtractor.FILE_LOCATION)

        model_class = conf.get('model_class', None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)
        self._load_csv()

    def _load_csv(self) -> None:
        """
        Create an iterator to execute sql.
        """
        if not hasattr(self, 'results'):
            with open(self.file_location, 'r') as fin:
                self.results = [dict(i) for i in csv.DictReader(fin)]

        if hasattr(self, 'model_class'):
            results = [self.model_class(**result)
                       for result in self.results]
        else:
            results = self.results
        self.iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self.iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.csv'


class CsvTableBadgeExtractor(Extractor):
    # Config keys
    TABLE_FILE_LOCATION = 'table_file_location'
    BADGE_FILE_LOCATION = 'badge_file_location'
    BADGE_SEPARATOR = 'badge_separator'

    """
    An Extractor that combines Table and Badge CSVs.
    """
    def init(self, conf: ConfigTree) -> None:
        self.conf = conf
        self.table_file_location = conf.get_string(CsvTableBadgeExtractor.TABLE_FILE_LOCATION)
        self.badge_file_location = conf.get_string(CsvTableBadgeExtractor.BADGE_FILE_LOCATION)
        self.badge_separator = conf.get_string(CsvTableBadgeExtractor.BADGE_SEPARATOR, default=',')
        self._load_csv()

    def _get_key(self,
                 db: str,
                 cluster: str,
                 schema: str,
                 tbl: str
                 ) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=db,
                                                     cluster=cluster,
                                                     schema=schema,
                                                     tbl=tbl)

    def _load_csv(self) -> None:
        with open(self.badge_file_location, 'r') as fin:
            self.badges = [dict(i) for i in csv.DictReader(fin)]
        # print("BADGES: " + str(self.badges))

        parsed_badges = defaultdict(list)
        for badge_dict in self.badges:
            db = badge_dict['database']
            cluster = badge_dict['cluster']
            schema = badge_dict['schema']
            table_name = badge_dict['table_name']
            id = self._get_key(db, cluster, schema, table_name)
            split_badges = split_badge_list(badges=badge_dict['name'],
                                            separator=self.badge_separator)
            for badge_name in split_badges:
                badge = Badge(name=badge_name, category=badge_dict['category'])
                parsed_badges[id].append(badge)

        with open(self.table_file_location, 'r') as fin:
            tables = [dict(i) for i in csv.DictReader(fin)]

        results = []
        for table_dict in tables:
            db = table_dict['database']
            cluster = table_dict['cluster']
            schema = table_dict['schema']
            table_name = table_dict['name']
            id = self._get_key(db, cluster, schema, table_name)
            badges = parsed_badges[id]

            if badges is None:
                badges = []
            badge_metadata = BadgeMetadata(start_label=TableMetadata.TABLE_NODE_LABEL,
                                           start_key=id,
                                           badges=badges)
            results.append(badge_metadata)
        self._iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.csvtablebadge'


class CsvTableColumnExtractor(Extractor):
    # Config keys
    TABLE_FILE_LOCATION = 'table_file_location'
    COLUMN_FILE_LOCATION = 'column_file_location'
    BADGE_SEPARATOR = 'badge_separator'

    """
    An Extractor that combines Table and Column CSVs.
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
        self.table_file_location = conf.get_string(CsvTableColumnExtractor.TABLE_FILE_LOCATION)
        self.column_file_location = conf.get_string(CsvTableColumnExtractor.COLUMN_FILE_LOCATION)
        self.badge_separator = conf.get_string(CsvTableBadgeExtractor.BADGE_SEPARATOR, default=',')
        self._load_csv()

    def _get_key(self,
                 db: str,
                 cluster: str,
                 schema: str,
                 tbl: str
                 ) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=db,
                                                     cluster=cluster,
                                                     schema=schema,
                                                     tbl=tbl)

    def _load_csv(self) -> None:
        """
        Create an iterator to execute sql.
        """
        with open(self.column_file_location, 'r') as fin:
            self.columns = [dict(i) for i in csv.DictReader(fin)]

        parsed_columns = defaultdict(list)
        for column_dict in self.columns:
            db = column_dict['database']
            cluster = column_dict['cluster']
            schema = column_dict['schema']
            table_name = column_dict['table_name']
            id = self._get_key(db, cluster, schema, table_name)
            split_badges = split_badge_list(badges=column_dict['badges'],
                                            separator=self.badge_separator)
            column = ColumnMetadata(
                name=column_dict['name'],
                description=column_dict['description'],
                col_type=column_dict['col_type'],
                sort_order=int(column_dict['sort_order']),
                badges=split_badges
            )
            parsed_columns[id].append(column)

        # Create Table Dictionary
        with open(self.table_file_location, 'r') as fin:
            tables = [dict(i) for i in csv.DictReader(fin)]

        results = []
        for table_dict in tables:
            db = table_dict['database']
            cluster = table_dict['cluster']
            schema = table_dict['schema']
            table_name = table_dict['name']
            id = self._get_key(db, cluster, schema, table_name)
            columns = parsed_columns[id]
            if columns is None:
                columns = []
            table = TableMetadata(database=table_dict['database'],
                                  cluster=table_dict['cluster'],
                                  schema=table_dict['schema'],
                                  name=table_dict['name'],
                                  description=table_dict['description'],
                                  columns=columns,
                                  # TODO: this possibly should parse stringified booleans;
                                  # right now it only will be false for empty strings
                                  is_view=bool(table_dict['is_view']),
                                  tags=table_dict['tags']
                                  )
            results.append(table)
        self._iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.csvtablecolumn'


class CsvTableLineageExtractor(Extractor):
    # Config keys
    TABLE_LINEAGE_FILE_LOCATION = 'table_lineage_file_location'

    """
    An Extractor that creates Table Lineage between two tables
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
        self.table_lineage_file_location = conf.get_string(CsvTableLineageExtractor.TABLE_LINEAGE_FILE_LOCATION)
        self._load_csv()

    def _load_csv(self) -> None:
        """
        Create an iterator to execute sql.
        """

        with open(self.table_lineage_file_location, 'r') as fin:
            self.table_lineage = [dict(i) for i in csv.DictReader(fin)]

        results = []
        for lineage_dict in self.table_lineage:
            source_table_key = lineage_dict['source_table_key']
            target_table_key = lineage_dict['target_table_key']
            lineage = TableLineage(
                table_key=source_table_key,
                downstream_deps=[target_table_key]
            )
            results.append(lineage)

        self._iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.csvtablelineage'


class CsvColumnLineageExtractor(Extractor):
    # Config keys
    COLUMN_LINEAGE_FILE_LOCATION = 'column_lineage_file_location'

    """
    An Extractor that creates Column Lineage between two columns
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
        self.column_lineage_file_location = conf.get_string(CsvColumnLineageExtractor.COLUMN_LINEAGE_FILE_LOCATION)
        self._load_csv()

    def _load_csv(self) -> None:
        """
        Create an iterator to execute sql.
        """

        with open(self.column_lineage_file_location, 'r') as fin:
            self.column_lineage = [dict(i) for i in csv.DictReader(fin)]

        results = []
        for lineage_dict in self.column_lineage:
            source_column_key = lineage_dict['source_column_key']
            target_column_key = lineage_dict['target_column_key']
            lineage = ColumnLineage(
                column_key=source_column_key,
                downstream_deps=[target_column_key]
            )
            results.append(lineage)

        self._iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.csvcolumnlineage'


class CsvTableQueryExtractor(Extractor):
    # Config keys
    TABLE_FILE_LOCATION = 'table_file_location'
    COLUMN_FILE_LOCATION = 'column_file_location'
    QUERY_FILE_LOCATION = 'query_file_location'
    USER_FILE_LOCATION = 'user_file_location'
    BADGE_SEPARATOR = 'badge_separator'
    TABLE_SEPARATOR = 'table_separator'

    """
    An Extractor that combines Table, Column, User and Query CSVs.
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
        self.user_file_location = conf.get_string(CsvTableQueryExtractor.USER_FILE_LOCATION)
        self.column_file_location = conf.get_string(CsvTableQueryExtractor.COLUMN_FILE_LOCATION)
        self.table_file_location = conf.get_string(CsvTableQueryExtractor.TABLE_FILE_LOCATION)
        self.query_file_location = conf.get_string(CsvTableQueryExtractor.QUERY_FILE_LOCATION)
        self.badge_separator = conf.get_string(CsvTableQueryExtractor.BADGE_SEPARATOR, default=',')
        self.table_separator = conf.get_string(CsvTableQueryExtractor.TABLE_SEPARATOR, default=',')

        self._load_csv()

    def _get_key(self,
                 db: str,
                 cluster: str,
                 schema: str,
                 tbl: str
                 ) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=db,
                                                     cluster=cluster,
                                                     schema=schema,
                                                     tbl=tbl)

    def _load_csv(self) -> None:
        """
        Create an iterator to execute sql.
        """
        with open(self.user_file_location, 'r') as fin:
            self.users = [dict(i) for i in csv.DictReader(fin)]

        parsed_users = dict()
        for user_dict in self.users:
            user = UserMetadata(
                email=user_dict['email'],
                first_name=user_dict['first_name'],
                last_name=user_dict['last_name'],
                full_name=user_dict['full_name'],
                github_username=user_dict['github_username'],
                team_name=user_dict['team_name'],
                employee_type=user_dict['employee_type'],
                manager_email=user_dict['manager_email'],
                slack_id=user_dict['slack_id'],
                role_name=user_dict['role_name']
            )
            parsed_users[user_dict['email']] = user

        with open(self.column_file_location, 'r') as fin:
            self.columns = [dict(i) for i in csv.DictReader(fin)]

        parsed_columns = defaultdict(list)
        for column_dict in self.columns:
            db = column_dict['database']
            cluster = column_dict['cluster']
            schema = column_dict['schema']
            table_name = column_dict['table_name']
            id = self._get_key(db, cluster, schema, table_name)
            split_badges = split_badge_list(badges=column_dict['badges'],
                                            separator=self.badge_separator)
            column = ColumnMetadata(
                name=column_dict['name'],
                description=column_dict['description'],
                col_type=column_dict['col_type'],
                sort_order=int(column_dict['sort_order']),
                badges=split_badges
            )
            parsed_columns[id].append(column)

        # Create Table Dictionary
        with open(self.table_file_location, 'r') as fin:
            self.tables = [dict(i) for i in csv.DictReader(fin)]

        parsed_tables = dict()
        for table_dict in self.tables:
            db = table_dict['database']
            cluster = table_dict['cluster']
            schema = table_dict['schema']
            table_name = table_dict['name']
            id = self._get_key(db, cluster, schema, table_name)
            columns = parsed_columns[id]
            if columns is None:
                columns = []
            table = TableMetadata(database=table_dict['database'],
                                  cluster=table_dict['cluster'],
                                  schema=table_dict['schema'],
                                  name=table_dict['name'],
                                  description=table_dict['description'],
                                  columns=columns,
                                  # TODO: this possibly should parse stringified booleans;
                                  # right now it only will be false for empty strings
                                  is_view=bool(table_dict['is_view']),
                                  tags=table_dict['tags']
                                  )
            parsed_tables[id] = table

        with open(self.query_file_location, 'r') as fin:
            self.queries = [dict(i) for i in csv.DictReader(fin)]
        results = []
        for query_dict in self.queries:
            sql = query_dict['sql']
            user = parsed_users[query_dict['user']]
            split_tables = split_table_list(tables=query_dict['tables'],
                                            separator=self.table_separator)
            tables = [parsed_tables[t] for t in split_tables]
            query = QueryMetadata(
                sql=sql,
                tables=tables,
                user=user)
            results.append(query)
        self._iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.csvtablequery'

class CsvTableQueryJoinExtractor(Extractor):
    # Config keys
    TABLE_FILE_LOCATION = 'table_file_location'
    COLUMN_FILE_LOCATION = 'column_file_location'
    QUERY_FILE_LOCATION = 'query_file_location'
    USER_FILE_LOCATION = 'user_file_location'
    JOIN_FILE_LOCATION = 'join_file_location'
    BADGE_SEPARATOR = 'badge_separator'
    TABLE_SEPARATOR = 'table_separator'

    """
    An Extractor that combines Table, Column, User and Query CSVs.
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
        self.user_file_location = conf.get_string(CsvTableQueryJoinExtractor.USER_FILE_LOCATION)
        self.column_file_location = conf.get_string(CsvTableQueryJoinExtractor.COLUMN_FILE_LOCATION)
        self.table_file_location = conf.get_string(CsvTableQueryJoinExtractor.TABLE_FILE_LOCATION)
        self.query_file_location = conf.get_string(CsvTableQueryJoinExtractor.QUERY_FILE_LOCATION)
        self.join_file_location = conf.get_string(CsvTableQueryJoinExtractor.JOIN_FILE_LOCATION)
        self.badge_separator = conf.get_string(CsvTableQueryJoinExtractor.BADGE_SEPARATOR, default=',')
        self.table_separator = conf.get_string(CsvTableQueryJoinExtractor.TABLE_SEPARATOR, default=',')

        self._load_csv()

    def _get_key(self,
                 db: str,
                 cluster: str,
                 schema: str,
                 tbl: str
                 ) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=db,
                                                     cluster=cluster,
                                                     schema=schema,
                                                     tbl=tbl)

    def _load_csv(self) -> None:
        """
        Create an iterator to execute sql.
        """
        with open(self.user_file_location, 'r') as fin:
            self.users = [dict(i) for i in csv.DictReader(fin)]

        parsed_users = dict()
        for user_dict in self.users:
            user = UserMetadata(
                email=user_dict['email'],
                first_name=user_dict['first_name'],
                last_name=user_dict['last_name'],
                full_name=user_dict['full_name'],
                github_username=user_dict['github_username'],
                team_name=user_dict['team_name'],
                employee_type=user_dict['employee_type'],
                manager_email=user_dict['manager_email'],
                slack_id=user_dict['slack_id'],
                role_name=user_dict['role_name']
            )
            parsed_users[user_dict['email']] = user

        with open(self.column_file_location, 'r') as fin:
            self.columns = [dict(i) for i in csv.DictReader(fin)]

        # Create Column Dictionary
        parsed_columns = defaultdict(list)
        parsed_columns_dict = dict()
        for column_dict in self.columns:
            db = column_dict['database']
            cluster = column_dict['cluster']
            schema = column_dict['schema']
            table_name = column_dict['table_name']
            id = self._get_key(db, cluster, schema, table_name)
            split_badges = split_badge_list(badges=column_dict['badges'],
                                            separator=self.badge_separator)
            column = ColumnMetadata(
                name=column_dict['name'],
                description=column_dict['description'],
                col_type=column_dict['col_type'],
                sort_order=int(column_dict['sort_order']),
                badges=split_badges
            )
            parsed_columns[id].append(column)
            parsed_columns_dict[f'{ id }/{ column_dict["name"] }'] = column

        # Create Table Dictionary
        with open(self.table_file_location, 'r') as fin:
            self.tables = [dict(i) for i in csv.DictReader(fin)]

        parsed_tables = dict()
        for table_dict in self.tables:
            db = table_dict['database']
            cluster = table_dict['cluster']
            schema = table_dict['schema']
            table_name = table_dict['name']
            id = self._get_key(db, cluster, schema, table_name)
            columns = parsed_columns[id]
            if columns is None:
                columns = []
            table = TableMetadata(database=table_dict['database'],
                                  cluster=table_dict['cluster'],
                                  schema=table_dict['schema'],
                                  name=table_dict['name'],
                                  description=table_dict['description'],
                                  columns=columns,
                                  # TODO: this possibly should parse stringified booleans;
                                  # right now it only will be false for empty strings
                                  is_view=bool(table_dict['is_view']),
                                  tags=table_dict['tags']
                                  )
            parsed_tables[id] = table

        # Create Query Dictionary

        with open(self.query_file_location, 'r') as fin:
            self.queries = [dict(i) for i in csv.DictReader(fin)]
        parsed_queries = {}
        for query_dict in self.queries:
            sql = query_dict['sql']
            user = parsed_users[query_dict['user']]
            split_tables = split_table_list(tables=query_dict['tables'],
                                            separator=self.table_separator)
            tables = [parsed_tables[t] for t in split_tables]
            query = QueryMetadata(
                sql=sql,
                tables=tables,
                user=user)
            parsed_queries[sql] = query

        with open(self.join_file_location, 'r') as fin:
            self.joins = [dict(i) for i in csv.DictReader(fin)]
        results = []
        for join_dict in self.joins:
            join = QueryJoinMetadata(
                left_table=parsed_tables[join_dict['left_table']],
                right_table=parsed_tables[join_dict['right_table']],
                left_column=parsed_columns_dict[join_dict['left_column']],
                right_column=parsed_columns_dict[join_dict['right_column']],
                join_type=join_dict['join_type'],
                join_operator=join_dict['join_operator'],
                join_sql=join_dict['join_sql'],
                query_metadata=parsed_queries[join_dict['join_sql']])
            results.append(join)
        self._iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.csvtablequeryjoin'


class CsvTableQueryWhereExtractor(Extractor):
    # Config keys
    TABLE_FILE_LOCATION = 'table_file_location'
    COLUMN_FILE_LOCATION = 'column_file_location'
    QUERY_FILE_LOCATION = 'query_file_location'
    USER_FILE_LOCATION = 'user_file_location'
    WHERE_FILE_LOCATION = 'where_file_location'
    BADGE_SEPARATOR = 'badge_separator'
    TABLE_SEPARATOR = 'table_separator'

    """
    An Extractor that combines Table, Column, User and Query CSVs.
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
        self.user_file_location = conf.get_string(CsvTableQueryWhereExtractor.USER_FILE_LOCATION)
        self.column_file_location = conf.get_string(CsvTableQueryWhereExtractor.COLUMN_FILE_LOCATION)
        self.table_file_location = conf.get_string(CsvTableQueryWhereExtractor.TABLE_FILE_LOCATION)
        self.query_file_location = conf.get_string(CsvTableQueryWhereExtractor.QUERY_FILE_LOCATION)
        self.where_file_location = conf.get_string(CsvTableQueryWhereExtractor.WHERE_FILE_LOCATION)
        self.badge_separator = conf.get_string(CsvTableQueryWhereExtractor.BADGE_SEPARATOR, default=',')
        self.table_separator = conf.get_string(CsvTableQueryWhereExtractor.TABLE_SEPARATOR, default=',')

        self._load_csv()

    def _get_key(self,
                 db: str,
                 cluster: str,
                 schema: str,
                 tbl: str
                 ) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=db,
                                                     cluster=cluster,
                                                     schema=schema,
                                                     tbl=tbl)

    def _load_csv(self) -> None:
        """
        Create an iterator to execute sql.
        """
        with open(self.user_file_location, 'r') as fin:
            self.users = [dict(i) for i in csv.DictReader(fin)]

        parsed_users = dict()
        for user_dict in self.users:
            user = UserMetadata(
                email=user_dict['email'],
                first_name=user_dict['first_name'],
                last_name=user_dict['last_name'],
                full_name=user_dict['full_name'],
                github_username=user_dict['github_username'],
                team_name=user_dict['team_name'],
                employee_type=user_dict['employee_type'],
                manager_email=user_dict['manager_email'],
                slack_id=user_dict['slack_id'],
                role_name=user_dict['role_name']
            )
            parsed_users[user_dict['email']] = user

        with open(self.column_file_location, 'r') as fin:
            self.columns = [dict(i) for i in csv.DictReader(fin)]

        # Create Column Dictionary
        parsed_columns = defaultdict(list)
        parsed_columns_dict = dict()
        for column_dict in self.columns:
            db = column_dict['database']
            cluster = column_dict['cluster']
            schema = column_dict['schema']
            table_name = column_dict['table_name']
            id = self._get_key(db, cluster, schema, table_name)
            split_badges = split_badge_list(badges=column_dict['badges'],
                                            separator=self.badge_separator)
            column = ColumnMetadata(
                name=column_dict['name'],
                description=column_dict['description'],
                col_type=column_dict['col_type'],
                sort_order=int(column_dict['sort_order']),
                badges=split_badges
            )
            parsed_columns[id].append(column)
            parsed_columns_dict[f'{ id }/{ column_dict["name"] }'] = column

        # Create Table Dictionary
        with open(self.table_file_location, 'r') as fin:
            self.tables = [dict(i) for i in csv.DictReader(fin)]

        parsed_tables = dict()
        for table_dict in self.tables:
            db = table_dict['database']
            cluster = table_dict['cluster']
            schema = table_dict['schema']
            table_name = table_dict['name']
            id = self._get_key(db, cluster, schema, table_name)
            columns = parsed_columns[id]
            if columns is None:
                columns = []
            table = TableMetadata(database=table_dict['database'],
                                  cluster=table_dict['cluster'],
                                  schema=table_dict['schema'],
                                  name=table_dict['name'],
                                  description=table_dict['description'],
                                  columns=columns,
                                  # TODO: this possibly should parse stringified booleans;
                                  # right now it only will be false for empty strings
                                  is_view=bool(table_dict['is_view']),
                                  tags=table_dict['tags']
                                  )
            parsed_tables[id] = table

        # Create Query Dictionary

        with open(self.query_file_location, 'r') as fin:
            self.queries = [dict(i) for i in csv.DictReader(fin)]
        parsed_queries = {}
        for query_dict in self.queries:
            sql = query_dict['sql']
            user = parsed_users[query_dict['user']]
            split_tables = split_table_list(tables=query_dict['tables'],
                                            separator=self.table_separator)
            tables = [parsed_tables[t] for t in split_tables]
            query = QueryMetadata(
                sql=sql,
                tables=tables,
                user=user)
            parsed_queries[sql] = query

        with open(self.where_file_location, 'r') as fin:
            self.wheres = [dict(i) for i in csv.DictReader(fin)]
        results = []
        for where_dict in self.wheres:
            query_metadata = parsed_queries[where_dict['sql']]
            where = QueryWhereMetadata(
                tables=query_metadata.tables,
                where_clause=where_dict['where_clause'],
                left_arg=where_dict['left_arg'],
                right_arg=where_dict['right_arg'],
                operator=where_dict['operator'],
                query_metadata=query_metadata)
            results.append(where)
        self._iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.csvtablequerywhere'


class CsvTableQueryExecutionExtractor(Extractor):
    # Config keys
    TABLE_FILE_LOCATION = 'table_file_location'
    COLUMN_FILE_LOCATION = 'column_file_location'
    QUERY_FILE_LOCATION = 'query_file_location'
    USER_FILE_LOCATION = 'user_file_location'
    EXECUTION_FILE_LOCATION = 'execution_file_location'
    BADGE_SEPARATOR = 'badge_separator'
    TABLE_SEPARATOR = 'table_separator'

    """
    An Extractor that combines Table, Column, User and Query CSVs.
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
        self.user_file_location = conf.get_string(CsvTableQueryExecutionExtractor.USER_FILE_LOCATION)
        self.column_file_location = conf.get_string(CsvTableQueryExecutionExtractor.COLUMN_FILE_LOCATION)
        self.table_file_location = conf.get_string(CsvTableQueryExecutionExtractor.TABLE_FILE_LOCATION)
        self.query_file_location = conf.get_string(CsvTableQueryExecutionExtractor.QUERY_FILE_LOCATION)
        self.execution_file_location = conf.get_string(CsvTableQueryExecutionExtractor.EXECUTION_FILE_LOCATION)
        self.badge_separator = conf.get_string(CsvTableQueryExecutionExtractor.BADGE_SEPARATOR, default=',')
        self.table_separator = conf.get_string(CsvTableQueryExecutionExtractor.TABLE_SEPARATOR, default=',')

        self._load_csv()

    def _get_key(self,
                 db: str,
                 cluster: str,
                 schema: str,
                 tbl: str
                 ) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=db,
                                                     cluster=cluster,
                                                     schema=schema,
                                                     tbl=tbl)

    def _load_csv(self) -> None:
        """
        Create an iterator to execute sql.
        """
        with open(self.user_file_location, 'r') as fin:
            self.users = [dict(i) for i in csv.DictReader(fin)]

        parsed_users = dict()
        for user_dict in self.users:
            user = UserMetadata(
                email=user_dict['email'],
                first_name=user_dict['first_name'],
                last_name=user_dict['last_name'],
                full_name=user_dict['full_name'],
                github_username=user_dict['github_username'],
                team_name=user_dict['team_name'],
                employee_type=user_dict['employee_type'],
                manager_email=user_dict['manager_email'],
                slack_id=user_dict['slack_id'],
                role_name=user_dict['role_name']
            )
            parsed_users[user_dict['email']] = user

        with open(self.column_file_location, 'r') as fin:
            self.columns = [dict(i) for i in csv.DictReader(fin)]

        parsed_columns = defaultdict(list)
        for column_dict in self.columns:
            db = column_dict['database']
            cluster = column_dict['cluster']
            schema = column_dict['schema']
            table_name = column_dict['table_name']
            id = self._get_key(db, cluster, schema, table_name)
            split_badges = split_badge_list(badges=column_dict['badges'],
                                            separator=self.badge_separator)
            column = ColumnMetadata(
                name=column_dict['name'],
                description=column_dict['description'],
                col_type=column_dict['col_type'],
                sort_order=int(column_dict['sort_order']),
                badges=split_badges
            )
            parsed_columns[id].append(column)

        # Create Table Dictionary
        with open(self.table_file_location, 'r') as fin:
            self.tables = [dict(i) for i in csv.DictReader(fin)]

        parsed_tables = dict()
        for table_dict in self.tables:
            db = table_dict['database']
            cluster = table_dict['cluster']
            schema = table_dict['schema']
            table_name = table_dict['name']
            id = self._get_key(db, cluster, schema, table_name)
            columns = parsed_columns[id]
            if columns is None:
                columns = []
            table = TableMetadata(database=table_dict['database'],
                                  cluster=table_dict['cluster'],
                                  schema=table_dict['schema'],
                                  name=table_dict['name'],
                                  description=table_dict['description'],
                                  columns=columns,
                                  # TODO: this possibly should parse stringified booleans;
                                  # right now it only will be false for empty strings
                                  is_view=bool(table_dict['is_view']),
                                  tags=table_dict['tags']
                                  )
            parsed_tables[id] = table

        # Create Query Dictionary

        with open(self.query_file_location, 'r') as fin:
            self.queries = [dict(i) for i in csv.DictReader(fin)]
        parsed_queries = {}
        for query_dict in self.queries:
            sql = query_dict['sql']
            user = parsed_users[query_dict['user']]
            split_tables = split_table_list(tables=query_dict['tables'],
                                            separator=self.table_separator)
            tables = [parsed_tables[t] for t in split_tables]
            query = QueryMetadata(
                sql=sql,
                tables=tables,
                user=user)
            parsed_queries[sql] = query

        with open(self.execution_file_location, 'r') as fin:
            self.executions = [dict(i) for i in csv.DictReader(fin)]
        results = []
        for execution_dict in self.executions:
            sql=execution_dict['sql']
            execution = QueryExecutionsMetadata(
                start_time=int(execution_dict['start_time']),
                execution_count=int(execution_dict['execution_count']),
                query_metadata=parsed_queries[sql])
            results.append(execution)
        self._iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.csvtablequeryexecution'
