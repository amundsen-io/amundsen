# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import pyparsing as pp

array_keyword = pp.Keyword('array')
row_keyword = pp.Keyword('row')
struct_keyword = pp.Keyword('struct')

nest_open = pp.Word('<([')
nest_close = pp.Word('>)]')

col_name = pp.Word(pp.alphanums + '_')
col_type = pp.Forward()
col_type_delimiter = pp.Word(':') | pp.White(' ')
column = col_name('name') + col_type_delimiter + col_type('type')
col_list = pp.delimitedList(pp.Group(column))

scalar_type = pp.Word(pp.alphas)

struct_type = pp.locatedExpr(pp.nestedExpr(
    opener=struct_keyword + nest_open, closer=nest_close, content=col_list | col_type, ignoreExpr=None
))

row_type = pp.locatedExpr(pp.nestedExpr(
    opener=row_keyword + nest_open, closer=nest_close, content=col_list | col_type, ignoreExpr=None
))

array_type = pp.locatedExpr(pp.nestedExpr(
    opener=array_keyword + nest_open, closer=nest_close, content=col_type, ignoreExpr=None
))

col_type <<= struct_type('children') | array_type('children') | row_type('children') | scalar_type('type')


def _separate_double_brackets(type_str: str) -> str:
    """
    Double close brackets seem to break the parsing so this
    adds a space between and fixes it.
    'array<struct<col:type>>' --> 'array<struct<col:type> >'
    """
    type_str = type_str.replace(">", "> ")
    type_str = type_str.replace(")", ") ")
    type_str = type_str.replace("]", "] ")
    return type_str


def _combine_double_brackets(type_str: str) -> str:
    type_str = type_str.replace("> ", ">")
    type_str = type_str.replace(") ", ")")
    type_str = type_str.replace("] ", "]")
    return type_str


def get_original_text(parsed_results, original_text):
    if 'locn_start' in parsed_results and 'locn_end' in parsed_results:
        return original_text[parsed_results['locn_start']:parsed_results['locn_end']]
    return None


def parse_col_type_string(type_str: str) -> pp.ParseResults:
    return col_type.parseString(type_str, parseAll=True)


def extract_columns_from_dict(column_name: str, parsed_results: dict, original_text: str):
    results = []
    type = parsed_results.get('type', '')
    if type != '':
        results.append({
            'name': column_name,
            'full_name': column_name,
            'col_type': type
        })
    elif 'children' in parsed_results:
        _extract_columns_from_dict_helper('', column_name, parsed_results['children'], original_text, results)
    return results


def _extract_columns_from_dict_helper(base_name: str,
                                      col_name: str,
                                      parsed_obj: dict,
                                      original_text: str,
                                      results: list):
    def _handle_column_object(col_object):
        name = col_object.get('name', '')
        children = col_object.get('children', [])
        if children:
            _extract_columns_from_dict_helper(full_name, name, children, original_text, results)
        if name != '' and 'type' in col_object:
            if type(col_object['type']) is str:
                results.append({
                    'name': name,
                    'full_name': full_name + '.' + name,
                    'col_type': col_object['type']
                })

    full_name = '.'.join(filter(None, (base_name, col_name)))
    matched_text = _combine_double_brackets(get_original_text(parsed_obj, original_text))
    if 'value' in parsed_obj:
        # locatedExpr wraps the result in a 'value'
        # The parser then wraps it in another array so we can flatten that
        parsed_obj = parsed_obj['value'][0]

    if col_name != '':
        # Skips the second instance of double-nested columns such as 'array<struct<...>>'
        results.append({
            'name': col_name,
            'full_name': full_name,
            'col_type': matched_text
        })

    if type(parsed_obj) is list:
        for col_obj in parsed_obj:
            _handle_column_object(col_obj)
    else:
        _handle_column_object(parsed_obj)


def get_columns_from_type(col_name: str, col_type: str):
    prepped_col_type = _separate_double_brackets(col_type)
    parsed_results = parse_col_type_string(prepped_col_type)
    dictionary = parsed_results.asDict()
    return extract_columns_from_dict(col_name, dictionary, prepped_col_type)
