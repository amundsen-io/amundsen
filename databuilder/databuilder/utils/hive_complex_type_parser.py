# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Union

from amundsen_common.models.table import TypeMetadata
from databuilder.models.table_metadata import ColumnMetadata
from databuilder.utils.base_complex_type_parser import ComplexTypeParser, ComplexTypeParserConfig


class ComplexHiveParser(ComplexTypeParserConfig):
    name = "HiveComplexTypeParser"


def parse_hive_type(type_str: str, name: str, parent: Union[ColumnMetadata, TypeMetadata]) -> TypeMetadata:
    parser = ComplexTypeParser(ComplexHiveParser())
    return parser.parse_type(type_str, name, parent)
