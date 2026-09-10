# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging
from typing import Any

from pyhocon import ConfigTree

from databuilder.models.table_metadata import TableMetadata
from databuilder.models.type_metadata import ScalarTypeMetadata
from databuilder.transformer.base_transformer import Transformer

PARSING_FUNCTION = 'parsing_function'

LOGGER = logging.getLogger(__name__)


class ComplexTypeTransformer(Transformer):
    """
    Transforms complex types for columns in a table.
    Takes a TableMetadata object and iterates over the columns.
    The configured parser takes each column's type string, name,
    and the column itself, and sets the column's type_metadata
    field with the parsed results contained in a TypeMetadata object.
    """
    def init(self, conf: ConfigTree) -> None:
        self.success_count = 0
        self.failure_count = 0

        parsing_function = conf.get_string(PARSING_FUNCTION)
        module_name, function_name = parsing_function.rsplit(".", 1)
        mod = importlib.import_module(module_name)
        self._parsing_function = getattr(mod, function_name)

    def transform(self, record: Any) -> TableMetadata:
        if not isinstance(record, TableMetadata):
            raise Exception(f"ComplexTypeTransformer expects record of type TableMetadata, received {type(record)}")

        for column in record.columns:
            try:
                column.set_column_key(record._get_col_key(column))
                column.set_type_metadata(self._parsing_function(column.type, column.name, column))
            except Exception as e:
                # Default to scalar type if the type string cannot be parsed
                column.set_type_metadata(ScalarTypeMetadata(name=column.name, parent=column, type_str=column.type))
                self.failure_count += 1
                LOGGER.warning(f"Could not parse type for column {column.name} in table {record.name}: {e}")
            else:
                self.success_count += 1

        return record

    def get_scope(self) -> str:
        return 'transformer.complex_type'
