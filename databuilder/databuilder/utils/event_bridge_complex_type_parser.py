# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from pyparsing import (
    Group, OneOrMore, Optional, Word, alphanums, delimitedList, nestedExpr, originalTextFor, Keyword,
)

from amundsen_common.models.table import TypeMetadata
from databuilder.utils.base_complex_type_parser import ComplexTypeParser, ComplexTypeParserConfig


class ComplexEventBridgeParser(ComplexTypeParserConfig):

    def __init__(self):

        # init the struct_with_name_type nested Expression
        self.struct_with_name_type: nestedExpr = self.struct_type

        self.set_custom_extractors()

        # Set the sequence field types to look for
        self.field_type <<= originalTextFor(
            self.array_type | self.struct_type | self.struct_with_name_type | self.scalar_type)

        # set the sequence of complex type expressions
        self.complex_type = (self.array_type("array_type") | self.struct_type("struct_type") |
                             self.struct_with_name_type("struct_type") | self.scalar_type("scalar_type"))

    def set_custom_extractors(self):
        self.field_name = Word(alphanums + "_" + '-')

        self.set_scalar_type()
        self.set_struct_type()

    # Take inputs in the shape
    # "[DateTime]"
    def set_scalar_type(self):
        scalar_quantifier = "[" + self.field_name + Optional(
            "]" | "," + self.field_name + "]")
        self.scalar_type = OneOrMore(self.field_name) + Optional(scalar_quantifier)

    # Take inputs in the shape
    # "struct<nest1:int,nest2:int>"
    # "struct<object>
    def set_struct_type(self) -> nestedExpr:

        struct_field = self.field_name + ":" + self.field_type("type") | self.field_type
        struct_list = delimitedList(Group(struct_field))
        struct_keyword = Keyword("struct")

        self.struct_type = nestedExpr(
            opener=struct_keyword + "<", closer=">", content=struct_list, ignoreExpr=None
        )

        self.struct_with_name_type = nestedExpr(
            opener=self.field_name("name") + ":" + struct_keyword + "<", closer=">", content=
            self.struct_list, ignoreExpr=None
        )


def parse_event_bridge_type(type_str: str, name: str,
                            parent) -> TypeMetadata:
    parser = ComplexTypeParser(ComplexEventBridgeParser())

    return parser.parse_type(type_str, name, parent)
