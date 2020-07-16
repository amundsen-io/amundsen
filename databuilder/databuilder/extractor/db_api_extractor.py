# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging
from typing import Iterable, Any  # noqa: F401

from pyhocon import ConfigTree  # noqa: F401

from databuilder.extractor.base_extractor import Extractor


LOGGER = logging.getLogger(__name__)


class DBAPIExtractor(Extractor):
    """
    Generic DB API extractor.
    """
    CONNECTION_CONFIG_KEY = 'connection'
    SQL_CONFIG_KEY = 'sql'

    def init(self, conf):
        # type: (ConfigTree) -> None
        """
        Receives a {Connection} object and {sql} to execute.
        An optional model class can be passed, in which, sql result row
        would be converted to a class instance and returned to calling
        function
        :param conf:
        :return:
        """
        self.conf = conf
        self.connection = conf.get(DBAPIExtractor.CONNECTION_CONFIG_KEY)  # type: Any
        self.cursor = self.connection.cursor()
        self.sql = conf.get(DBAPIExtractor.SQL_CONFIG_KEY)

        model_class = conf.get('model_class', None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)

        self._iter = iter(self._execute_query())

    def _execute_query(self):
        # type: () -> Iterable[Any]
        """
        Use cursor to execute the {sql}
        :return:
        """
        LOGGER.info('Executing query: \n{}'.format(self.sql))
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()

    def extract(self):
        # type: () -> Any
        """
        Fetch one sql result row, convert to {model_class} if specified before
        returning.
        :return:
        """

        try:
            result = next(self._iter)
        except StopIteration:
            return None

        if hasattr(self, 'model_class'):
            obj = self.model_class(*result[:len(result)])
            return obj
        else:
            return result

    def close(self):
        # type: () -> None
        """
        close cursor and connection handlers
        :return:
        """
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            LOGGER.warning("Exception encountered while closing up connection handler!", e)

    def get_scope(self):
        # type: () -> str
        return 'extractor.dbapi'
