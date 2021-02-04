# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import importlib
from typing import Any

from pyhocon import ConfigTree
from sqlalchemy import create_engine

from databuilder.extractor.base_extractor import Extractor


class SQLAlchemyExtractor(Extractor):
    # Config keys
    CONN_STRING = 'conn_string'
    EXTRACT_SQL = 'extract_sql'
    CONNECT_ARGS = 'connect_args'
    """
    An Extractor that extracts records via SQLAlchemy. Database that supports SQLAlchemy can use this extractor
    """

    def init(self, conf: ConfigTree) -> None:
        """
        Establish connections and import data model class if provided
        :param conf:
        """
        self.conf = conf
        self.conn_string = conf.get_string(SQLAlchemyExtractor.CONN_STRING)

        self.connection = self._get_connection()

        self.extract_sql = conf.get_string(SQLAlchemyExtractor.EXTRACT_SQL)

        model_class = conf.get('model_class', None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)
        self._execute_query()

    def _get_connection(self) -> Any:
        """
        Create a SQLAlchemy connection to Database
        """
        connect_args = {
            k: v
            for k, v in self.conf.get_config(
                self.CONNECT_ARGS, default=ConfigTree()
            ).items()
        }
        engine = create_engine(self.conn_string, connect_args=connect_args)
        conn = engine.connect()
        return conn

    def _execute_query(self) -> None:
        """
        Create an iterator to execute sql.
        """
        if not hasattr(self, 'results'):
            self.results = self.connection.execute(self.extract_sql)

        if hasattr(self, 'model_class'):
            results = [self.model_class(**result)
                       for result in self.results]
        else:
            results = self.results
        self.iter = iter(results)

    def extract(self) -> Any:
        """
        Yield the sql result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self.iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.sqlalchemy'
