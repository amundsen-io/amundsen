# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, Tuple, Any

from pyhocon import ConfigTree

from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from databuilder.transformer.base_transformer import Transformer
from databuilder.utils.nested_column_parser import get_columns_from_type


class NestedColumnsTransformer(Transformer):
    """
    Checks Table Columns for complex types. These get parsed into individual columns that get added back
    """

    def init(self, conf: ConfigTree) -> None:
        pass

    def transform(self, record: TableMetadata) -> Any:
        columns = record.columns
        new_columns = []
        for column in columns:
            nested_columns = get_columns_from_type(column.COLUMN_NAME, column.COLUMN_TYPE)
            for nested_column in nested_columns[1:]:
                ColumnMetadata(nested_column['full_name'], None,
                               nested_column['col_type'], column.col_sort_order)
                new_columns.append(column)
        record.columns = columns + new_columns
        return record

    def get_scope(self) -> str:
        return 'transformer.nested_column_transformer'
