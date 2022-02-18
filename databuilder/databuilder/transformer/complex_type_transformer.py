# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import importlib
from typing import Any

from pyhocon import ConfigTree

from databuilder.models.table_metadata import TableMetadata
from databuilder.transformer.base_transformer import Transformer

PARSING_FUNCTION = 'parsing_function'


class ComplexTypeTransformer(Transformer):
    """
    Transforms complex types for columns in a table.
    Takes a TableMetadata object and iterates over the columns.
    The configured parser takes each column's type and key and sets the
    column's type_metadata field with the parsed results contained in a
    TypeMetadata object.
    """
    def init(self, conf: ConfigTree) -> None:
        try:
            parsing_function = conf.get_string(PARSING_FUNCTION)
            module_name, function_name = parsing_function.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self._parsing_function = getattr(mod, function_name)
        except (ValueError, ModuleNotFoundError, AttributeError):
            raise Exception("Invalid parsing function provided to ComplexTypeTransformer")

    def transform(self, record: Any) -> TableMetadata:
        if not isinstance(record, TableMetadata):
            raise Exception("ComplexTypeTransformer expects record of type TableMetadata")

        for column in record.columns:
            column.column_key = record._get_col_key(column)
            parsed_type_metadata = self._parsing_function(column)
            if parsed_type_metadata:
                column.type_metadata = parsed_type_metadata

        return record

    def get_scope(self) -> str:
        return 'transformer.complex_type'
