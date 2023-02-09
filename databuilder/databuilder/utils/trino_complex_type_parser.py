# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Union

from pyparsing import (
    Forward, Group, Keyword, OneOrMore, Optional, Word, alphanums, delimitedList, nestedExpr, nums, originalTextFor,
)

from databuilder.models.table_metadata import ColumnMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata, MapTypeMetadata, ScalarTypeMetadata, StructTypeMetadata, TypeMetadata,
)

array_keyword = Keyword("array")
map_keyword = Keyword("map")
struct_keyword = Keyword("row")

field_name = Word(alphanums + "_")
field_type = Forward()

# Scalar types
scalar_quantifier = "(" + Word(nums) + Optional(")" | "," + Word(nums) + ")")
scalar_type = OneOrMore(Word(alphanums + "_")) + Optional(scalar_quantifier)

# Complex types
array_field = "(" + field_type("type")
map_field = originalTextFor(scalar_type)("key") + "," + field_type("type")
struct_field = field_name("name") + field_type("type")
struct_list = delimitedList(Group(struct_field))
array_type = nestedExpr(
    opener=array_keyword, closer=")", content=array_field, ignoreExpr=None
)
map_type = nestedExpr(
    opener=map_keyword + "(", closer=")", content=map_field, ignoreExpr=None
)
struct_type = nestedExpr(
    opener=struct_keyword + "(", closer=")", content=struct_list, ignoreExpr=None
)

field_type <<= originalTextFor(array_type | map_type | struct_type | scalar_type)

complex_type = (array_type("array_type") | map_type("map_type") | struct_type("struct_type") |
                scalar_type("scalar_type"))


def parse_trino_type(type_str: str, name: str, parent: Union[ColumnMetadata, TypeMetadata]) -> TypeMetadata:
    type_str = type_str.lower()
    type_str = type_str.replace('\"', '')  # Remove quotes around names that are added when querying from HMS
    parsed_type = complex_type.parseString(type_str, parseAll=True)

    if parsed_type.scalar_type:
        return ScalarTypeMetadata(name=name,
                                  parent=parent,
                                  type_str=type_str)

    results = parsed_type[0]
    if parsed_type.array_type:
        array_type_metadata = ArrayTypeMetadata(name=name,
                                                parent=parent,
                                                type_str=type_str)
        array_inner_type = parse_trino_type(results.type, '_inner_', array_type_metadata)
        if not isinstance(array_inner_type, ScalarTypeMetadata):
            array_type_metadata.array_inner_type = array_inner_type
        return array_type_metadata
    elif parsed_type.map_type:
        map_type_metadata = MapTypeMetadata(name=name,
                                            parent=parent,
                                            type_str=type_str)
        map_type_metadata.map_key_type = parse_trino_type(results.key, '_map_key', map_type_metadata)
        map_type_metadata.map_value_type = parse_trino_type(results.type, '_map_value', map_type_metadata)
        return map_type_metadata
    elif parsed_type.struct_type:
        struct_type_metadata = StructTypeMetadata(name=name,
                                                  parent=parent,
                                                  type_str=type_str)
        struct_items = {}
        for index, result in enumerate(results):
            struct_items[result.name] = parse_trino_type(result.type, result.name, struct_type_metadata)
            struct_items[result.name].sort_order = index

        struct_type_metadata.struct_items = struct_items
        return struct_type_metadata
    else:
        raise Exception(f"Unrecognized type: {type_str}")
