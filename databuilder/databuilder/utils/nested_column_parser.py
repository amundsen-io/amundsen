from pyparsing import alphanums
from pyparsing import alphas
from pyparsing import delimitedList
from pyparsing import Forward
from pyparsing import Group
from pyparsing import Keyword
from pyparsing import nestedExpr
from pyparsing import ParseResults
from pyparsing import locatedExpr
from pyparsing import Word
from pyparsing import White

array_keyword = Keyword('array')
row_keyword = Keyword('row')
struct_keyword = Keyword('struct')

nest_open = Word('<([')
nest_close = Word('>)]')

col_name = Word(alphanums + '_')
col_type = Forward()
col_type_delimiter = Word(':') | White(' ')
column = col_name('name') + col_type_delimiter + col_type('type')
col_list = delimitedList(Group(column))

scalar_type = Word(alphas)

struct_type = locatedExpr(nestedExpr(
    opener=struct_keyword + nest_open, closer=nest_close, content=col_list | col_type, ignoreExpr=None
))

row_type = locatedExpr(nestedExpr(
    opener=row_keyword + nest_open, closer=nest_close, content=col_list | col_type, ignoreExpr=None
))

array_type = locatedExpr(nestedExpr(
    opener=array_keyword + nest_open, closer=nest_close, content=col_type, ignoreExpr=None
))

col_type <<= struct_type('struct') | array_type('array') | row_type('row') | scalar_type('type')


def _prep_nested_cols(type_str: str) -> str:
    """
    Double close brackets seem to break the parsing so this
    adds a space between and fixes it.
    'array<struct<col:type>>' --> 'array<struct<col:type> >'
    """
    type_str = type_str.replace(">", "> ")
    type_str = type_str.replace(")", ") ")
    type_str = type_str.replace("]", "] ")
    return type_str


def extract_original_text(parsed_results, original_text):
    if 'locn_start' in parsed_results and 'locn_end' in parsed_results:
        return original_text[parsed_results['locn_start']:parsed_results['locn_end']]
    return None


def parse_struct_inner_type_string(type_str: str) -> ParseResults:
    type_str = _prep_nested_cols(type_str)
    return col_type.parseString(type_str, parseAll=True)


def decorate_columns_dict(column_name: str, parsed_results: dict, original_text: str):
    results = []
    if 'type' in parsed_results:
        results.append({
            'name': column_name,
            'full_name': column_name,
            'col_type': parsed_results['type']
        })
    elif 'struct' in parsed_results:
        _decorate_columns_dict_helper('', column_name, parsed_results['struct'], original_text, results)
    elif 'row' in parsed_results:
        _decorate_columns_dict_helper('', column_name, parsed_results['row'], original_text, results)
    elif 'array' in parsed_results:
        _decorate_columns_dict_helper('', column_name, parsed_results['array'], original_text, results)
    return results


def _decorate_columns_dict_helper(base_name: str, col_name: str, parsed_obj: dict, original_text: str, results: list):
    matched_text = extract_original_text(parsed_obj, original_text)
    print('matched: ' + matched_text)
    if 'value' in parsed_obj:
        # locatedExpr wraps the result in a 'value'
        # The parser then wraps it in another array so we can flatten that
        parsed_obj = parsed_obj['value'][0]

    full_name = '.'.join(filter(None, (base_name, col_name)))
    if col_name is not '':
        # Skips the second instance of double-nested columns such as 'array<struct<...>>'
        results.append({
            'name': col_name,
            'full_name': full_name,
            'col_type': matched_text
        })

    if type(parsed_obj) is list:
        # TODO - cleanup by mergining the 'struct', 'array', and 'row' keywords
        # by modifying the `col_type` pyparsing definition above
        for result in parsed_obj:
            if 'name' in result and 'struct' in result:
                _decorate_columns_dict_helper(full_name, result['name'], result['struct'], original_text, results)
            if 'name' in result and 'array' in result:
                _decorate_columns_dict_helper(full_name, result['name'], result['array'], original_text, results)
            if 'name' in result and 'row' in result:
                _decorate_columns_dict_helper(full_name, result['name'], result['row'], original_text, results)
            if 'name' in result and 'type' in result:
                if type(result['type']) is str:
                    results.append({
                        'name': result['name'],
                        'full_name': full_name + '.' + result['name'],
                        'col_type': result['type']
                    })
    else:
        # TODO - Cleanup this reused code
        result = parsed_obj
        if 'struct' in result:
            _decorate_columns_dict_helper(full_name, '', result['struct'], original_text, results)
        if 'name' in result and 'array' in result:
            _decorate_columns_dict_helper(full_name, result['name'], result['array'], original_text, results)
        if 'name' in result and 'row' in result:
            _decorate_columns_dict_helper(full_name, result['name'], result['row'], original_text, results)
        if 'name' in result and 'type' in result:
            if type(result['type']) is str:
                results.append({
                    'name': result['name'],
                    'full_name': full_name + '.' + result['name'],
                    'col_type': result['type']
                })

def get_columns_from_type(col_name: str, col_type: str):
    parsed_results = parse_struct_inner_type_string(col_type)
    dictionary = parsed_results.asDict()
    return decorate_columns_dict(col_name, dictionary, col_type)
