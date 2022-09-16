import logging
from abc import ABC
from typing import Union

import pyparsing
from pyparsing import (
    Forward, Group, Keyword, OneOrMore, Optional, Word, alphanums, delimitedList, nestedExpr, originalTextFor, nums,
)

from databuilder.models.table_metadata import ColumnMetadata
from databuilder.models.type_metadata import (
    ArrayTypeMetadata, MapTypeMetadata, ScalarTypeMetadata, StructTypeMetadata, TypeMetadata,
)

LOGGER = logging.getLogger(__name__)


# ComplexTypeParser sets defaults for parsing structs (based on hive parser)
# depending on the source type keywords and default chars may change

class ComplexTypeParserConfig(ABC):
    field_type = Forward()

    # String words
    field_name = Word(alphanums + "_")

    # Union types
    # example "'nest2:uniontype<string,int>>'"
    union_keyword = Keyword("uniontype")
    union_list = delimitedList(field_type)
    union_type = nestedExpr(
        opener=union_keyword + "<", closer=">", content=union_list, ignoreExpr=None
    )

    # Scalar types mappings
    # example "(field)"
    scalar_quantifier = "(" + Word(nums) + Optional(")" | "," + Word(nums) + ")")
    scalar_type = union_type | OneOrMore(field_name) + Optional(scalar_quantifier)

    # Array types mappings
    # example "field<int>"
    str_array_inner_key = '_inner_'
    array_keyword = Keyword("array")
    array_field = "<" + field_type("type")

    array_type = nestedExpr(
        opener=array_keyword, closer=">", content=array_field, ignoreExpr=None
    )

    # Map types mappings
    # example "map<string,int>"
    map_keyword = Keyword("map")
    str_map_key = '_map_key'
    str_map_value = '_map_value'
    map_field = originalTextFor(scalar_type)("key") + "," + field_type("type")

    map_type = nestedExpr(
        opener=map_keyword + "<", closer=">", content=map_field, ignoreExpr=None
    )

    # struct types mappings
    # struct<nest1:int,nest2:int>
    struct_keyword = Keyword("struct")
    struct_field = field_name("name") + ":" + field_type("type")
    struct_list = delimitedList(Group(struct_field))

    struct_type = nestedExpr(
        opener=struct_keyword + "<", closer=">", content=struct_list, ignoreExpr=None
    )

    # combines the sequece of field
    field_type <<= originalTextFor(array_type | struct_type | map_type | scalar_type)

    complex_type = (array_type("array_type") | struct_type("struct_type") | map_type("map_type") |
                    scalar_type("scalar_type"))


class ComplexTypeParser:
    def __init__(self, parser_config: ComplexTypeParserConfig):
        self.parser_config = parser_config

    def parse_type(self, type_str: str, name: str, parent: Union[ColumnMetadata, TypeMetadata]) -> TypeMetadata:
        type_str = type_str.lower()
        parsed_type = self.parser_config.complex_type.parseString(type_str, parseAll=True)

        if parsed_type.scalar_type:
            return self._parse_scalar_type(name, parent, type_str)

        results = parsed_type[0]
        if parsed_type.array_type:
            return self._parse_array_type(name, parent, results, type_str)
        elif parsed_type.struct_type:
            return self._parse_struct_type(name, parent, results, type_str)
        elif parsed_type.map_type:
            return self._parse_map_type(name, parent, results, type_str)
        else:
            raise Exception(f"Unrecognized type: {type_str}")

    def _parse_struct_type(self, name, parent, results, type_str) -> StructTypeMetadata:
        struct_type_metadata = StructTypeMetadata(name=name,
                                                  parent=parent,
                                                  type_str=type_str)
        struct_items = {}
        for index, result in enumerate(results):
            if result.name:
                struct_items[result.name] = self.parse_type(result.type, result.name, struct_type_metadata)
                struct_items[result.name].sort_order = index
            else:
                result.name = "value"  # e.g struct<object> -> struct<value:object>
                result.type = result[0]
                struct_items[result.name] = self.parse_type(result.type, result.name, struct_type_metadata)
                struct_items[result.name].sort_order = 0

        struct_type_metadata.struct_items = struct_items
        return struct_type_metadata

    def _parse_map_type(self, name, parent, results, type_str) -> MapTypeMetadata:
        map_type_metadata = MapTypeMetadata(name=name,
                                            parent=parent,
                                            type_str=type_str)
        map_type_metadata.map_key_type = self.parse_type(results.key, self.parser_config.str_map_key, map_type_metadata)
        map_type_metadata.map_value_type = self.parse_type(results.type, self.parser_config.str_map_value,
                                                           map_type_metadata)
        return map_type_metadata

    def _parse_array_type(self, name, parent, results, type_str) -> ArrayTypeMetadata:
        array_type_metadata = ArrayTypeMetadata(name=name,
                                                parent=parent,
                                                type_str=type_str)
        array_inner_type = self.parse_type(results.type, self.parser_config.str_array_inner_key, array_type_metadata)
        if not isinstance(array_inner_type, ScalarTypeMetadata):
            array_type_metadata.array_inner_type = array_inner_type
        return array_type_metadata

    @staticmethod
    def _parse_scalar_type(name, parent, type_str) -> ScalarTypeMetadata:
        return ScalarTypeMetadata(name=name,
                                  parent=parent,
                                  type_str=type_str)
