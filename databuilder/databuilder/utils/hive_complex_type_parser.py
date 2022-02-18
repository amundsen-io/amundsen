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


def parse_hive_complex_type_string(column: ColumnMetadata) -> Union[TypeMetadata, None]:
    type_str = column.type.lower()
    parsed_type = (complex_type.parseString(type_str, parseAll=True)
                   if _is_complex_type(type_str) else None)
    if parsed_type:
        top_level_complex_type = parsed_type[0]
        type_metadata = _populate_nested_types(results=top_level_complex_type)
        type_metadata.name = f"type/{column.name}"
        _populate_parent_attribute(type_metadata, column)
        return type_metadata
    return None


def _create_type_metadata(result: ParseResults, inner_data_type: TypeMetadata) -> TypeMetadata:
    if result.name:
        # Struct child - set the name and return
        inner_data_type.name = result.name
        return inner_data_type
    elif result.key:
        # Map type
        inner_data_type.name = '_map_value'
        map_key_metadata = ScalarTypeMetadata(data_type=result.key,
                                              type_str=result.key)
        map_key_metadata.name = '_map_key'
        map_type_metadata = MapTypeMetadata(map_key=map_key_metadata,
                                            map_value=inner_data_type,
                                            type_str=f"map<{result.key},{inner_data_type}>")
        _populate_parent_attribute(map_key_metadata, map_type_metadata)
        _populate_parent_attribute(inner_data_type, map_type_metadata)
        return map_type_metadata
    else:
        # Array type
        inner_data_type.name = '_inner_'
        array_type_metadata = ArrayTypeMetadata(data_type=inner_data_type,
                                                type_str=f"array<{inner_data_type}>")
        _populate_parent_attribute(inner_data_type, array_type_metadata)
        return array_type_metadata


def _is_complex_type(col_type: str) -> bool:
    return (col_type.startswith('array<') or
            col_type.startswith('map<') or
            col_type.startswith('struct<'))


def _populate_nested_types(results: ParseResults) -> TypeMetadata:
    if results.type:
        # Array or Map type
        return _populate_type_helper(results)
    else:
        # Struct type
        struct_items = {}
        inner_string = ''
        sort_order = 0

        for result in results:
            struct_items[result.name] = _populate_type_helper(result)
            struct_items[result.name].sort_order = sort_order
            inner_string += f"{result.name}:{result.type},"
            sort_order += 1

        return StructTypeMetadata(struct_items=struct_items,
                                  type_str=f"struct<{inner_string[:-1]}>")


def _populate_type_helper(result: ParseResults) -> TypeMetadata:
    if not _is_complex_type(result.type):
        # Reached lowest level of nested types
        terminal_type = ScalarTypeMetadata(data_type=result.type,
                                           type_str=result.type)
        return _create_type_metadata(result, terminal_type)
    else:
        # Recursively populate the nested types
        next_parsed_type = complex_type.parseString(result.type, parseAll=True)
        inner_data_type = _populate_nested_types(results=next_parsed_type[0])

        type_metadata = _create_type_metadata(result, inner_data_type)
        _populate_parent_attribute(inner_data_type, type_metadata)
        return type_metadata


def _populate_parent_attribute(type_metadata: TypeMetadata, parent: Union[ColumnMetadata, TypeMetadata]) -> None:
    type_metadata.parent = parent

    if isinstance(type_metadata, StructTypeMetadata):
        for name, data_type in type_metadata.struct_items.items():
            data_type.parent = type_metadata
