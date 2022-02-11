# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Union

from pyparsing import (
    Forward, Group, Keyword, ParseResults, Word, alphanums, alphas, delimitedList, nestedExpr, originalTextFor,
)

from databuilder.models.table_metadata import ColumnMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata, MapTypeMetadata, ScalarTypeMetadata, StructTypeMetadata, TypeMetadata,
)

array_keyword = Keyword("array")
map_keyword = Keyword("map")
struct_keyword = Keyword("struct")

field_name = Word(alphanums + "_")
field_type = Forward()
array_field = "<" + field_type("type")
map_field = field_name("key") + "," + field_type("type")
struct_field = field_name("name") + ":" + field_type("type")
struct_list = delimitedList(Group(struct_field))

scalar_type = Word(alphas)
array_type = nestedExpr(
    opener=array_keyword, closer=">", content=array_field, ignoreExpr=None
)
map_type = nestedExpr(
    opener=map_keyword + "<", closer=">", content=map_field, ignoreExpr=None
)
struct_type = nestedExpr(
    opener=struct_keyword + "<", closer=">", content=struct_list, ignoreExpr=None
)

field_type <<= originalTextFor(array_type | map_type | struct_type | scalar_type)

complex_type = (array_type | map_type | struct_type)


def parse_hive_complex_type_string(type_str: str, column_key: str) -> Union[TypeMetadata, None]:
    type_str = type_str.lower()
    parsed_type = (complex_type.parseString(type_str, parseAll=True)
                   if _is_complex_type(type_str) else None)
    if parsed_type:
        top_level_complex_type = parsed_type[0]
        return _populate_nested_types(results=top_level_complex_type,
                                      start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                                      start_key=column_key)
    return None


def _create_type_metadata(result: ParseResults,
                          data_type: TypeMetadata,
                          start_label: str,
                          start_key: str) -> TypeMetadata:
    if result.name:
        return data_type
    elif result.key:
        return MapTypeMetadata(key=result.key,
                               value=data_type,
                               type_str=f"map<{result.key},{data_type}>",
                               start_label=start_label,
                               start_key=start_key)
    else:
        return ArrayTypeMetadata(data_type=data_type,
                                 type_str=f"array<{data_type}>",
                                 start_label=start_label,
                                 start_key=start_key)


def _get_next_start_key(result: ParseResults, start_key: str) -> str:
    if result.name:
        return f"{start_key}/{result.name}"
    elif result.key:
        return f"{start_key}/__map_inner"
    else:
        return f"{start_key}/__array_inner"


def _is_complex_type(col_type: str) -> bool:
    return (col_type.startswith('array<')
            or col_type.startswith('map<')
            or col_type.startswith('struct<'))


def _populate_nested_types(results: ParseResults, start_label: str, start_key: str) -> TypeMetadata:
    if results.type:
        # Array or Map type
        return _populate_type_helper(results, start_label, start_key)
    else:
        # Struct type
        struct_items = {}
        inner_string = ''
        for result in results:
            struct_items[result.name] = _populate_type_helper(result, start_label, start_key)
            inner_string += f"{result.name}:{result.type},"
        return StructTypeMetadata(struct_items=struct_items,
                                  type_str=f"struct<{inner_string[:-1]}>",
                                  start_label=start_label,
                                  start_key=start_key)


def _populate_type_helper(result: ParseResults,
                          start_label: str,
                          start_key: str) -> TypeMetadata:
    if not _is_complex_type(result.type):
        # Reached lowest level of nested types
        next_start_key = _get_next_start_key(result, start_key)
        terminal_type = ScalarTypeMetadata(data_type=result.type,
                                           type_str=result.type,
                                           start_label=TypeMetadata.NODE_LABEL,
                                           start_key=next_start_key)
        return _create_type_metadata(result, terminal_type, start_label, start_key)
    else:
        # Recursively populate the nested types
        next_parsed_type = complex_type.parseString(result.type, parseAll=True)
        next_start_key = _get_next_start_key(result, start_key)
        data_type = _populate_nested_types(results=next_parsed_type[0],
                                           start_label=TypeMetadata.NODE_LABEL,
                                           start_key=next_start_key)
        return _create_type_metadata(result, data_type, start_label, start_key)
