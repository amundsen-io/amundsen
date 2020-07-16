# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import csv
import importlib
from collections import defaultdict

from pyhocon import ConfigTree  # noqa: F401
from typing import Any, Iterator  # noqa: F401

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata


class CsvExtractor(Extractor):
    # Config keys
    FILE_LOCATION = 'file_location'

    """
    An Extractor that extracts records via CSV.
    """

    def init(self, conf):
        # type: (ConfigTree) -> None
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

    def _load_csv(self):
        # type: () -> None
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

    def extract(self):
        # type: () -> Any
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

    def get_scope(self):
        # type: () -> str
        return 'extractor.csv'


class CsvTableColumnExtractor(Extractor):
    # Config keys
    TABLE_FILE_LOCATION = 'table_file_location'
    COLUMN_FILE_LOCATION = 'column_file_location'

    """
    An Extractor that combines Table and Column CSVs.
    """

    def init(self, conf):
        # type: (ConfigTree) -> None
        """
        :param conf:
        """
        self.conf = conf
        self.table_file_location = conf.get_string(CsvTableColumnExtractor.TABLE_FILE_LOCATION)
        self.column_file_location = conf.get_string(CsvTableColumnExtractor.COLUMN_FILE_LOCATION)
        self._load_csv()

    def _get_key(self, db, cluster, schema, tbl):
        return TableMetadata.TABLE_KEY_FORMAT.format(db=db,
                                                     cluster=cluster,
                                                     schema=schema,
                                                     tbl=tbl)

    def _load_csv(self):
        # type: () -> None
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
            table = column_dict['table_name']
            id = self._get_key(db, cluster, schema, table)
            column = ColumnMetadata(
                name=column_dict['name'],
                description=column_dict['description'],
                col_type=column_dict['col_type'],
                sort_order=int(column_dict['sort_order'])
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
            table = table_dict['name']
            id = self._get_key(db, cluster, schema, table)
            columns = parsed_columns[id]
            if columns is None:
                columns = []
            table = TableMetadata(database=table_dict['database'],
                                  cluster=table_dict['cluster'],
                                  schema=table_dict['schema'],
                                  name=table_dict['name'],
                                  description=table_dict['description'],
                                  columns=columns,
                                  is_view=table_dict['is_view'],
                                  tags=table_dict['tags']
                                  )
            results.append(table)
        self._iter = iter(results)

    def extract(self):
        # type: () -> Any
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

    def get_scope(self):
        # type: () -> str
        return 'extractor.csvtablecolumn'
