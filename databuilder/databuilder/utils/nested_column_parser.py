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
    """
    example input:
    col1:struct<col2:struct<col3:int,col4:int>>,col5:int
    output:
    ParseResults([
        ParseResults(name:'col1', type:'struct<col2:struct<col3:int,col4:int>>'),
        ParseResults(name:'col5', type:'int')
    ])
    :param type_str:
    :return: ParseResults object
    """
    type_str = _prep_nested_cols(type_str)
    return col_type.parseString(type_str, parseAll=True)

#
# def _flatten_extra_array_wrapping(dict):
#     """
#     Each matched object in the parser adds another [] or {} to the parsed dictionary.
#     This function flattens extra wrappers recursively
#     """
#     if 'struct' in dict:
#         dict['struct'] = dict['struct'][0]
#         # The nested struct is expected to be a list
#         for struct in dict['struct']:
#             _flatten_extra_array_wrapping(struct)
#     if 'row' in dict:
#         dict['row'] = dict['row'][0]
#         # The nested row is expected to be a list
#         for row in dict['row']:
#             _flatten_extra_array_wrapping(row)
#     if 'array' in dict:
#         dict['array'] = dict['array'][0]
#         # The nested array is expected to have a single child
#         _flatten_extra_array_wrapping(dict['array'])


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

    full_name = base_name + '.' + col_name if base_name is not '' else col_name
    results.append({
        'name': col_name,
        'full_name': full_name,
        'col_type': matched_text
    })

    if type(parsed_obj) is list:
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


    # elif 'struct' in parsed_results:





test_strings = [
    "string",
    "array<string>",
    "struct<col_1:string, col_2:string>",
    "struct<col_1:string,col_2:string,col_3:bigint,col_4:struct<col_5:boolean,col_6:timestamp>>",
    "array<struct<col_1:string, col_2:int>>",
    "struct<col_1:struct<col_2:boolean,col_3:array<timestamp>>>",
    """
        array<struct<started_at:timestamp,ended_at:timestamp,type:string,distance:bigint,index:bigint,start_location:
        struct<lat:double,lng:double>,end_location:struct<lat:double,lng:double>,gql_object_id:string,end_reason:string>>
    """,
    "row(col_1:varchar, col_2:int, col_3:array(int))",
    "row(col_1 varchar, col_2 int, col_3 array(int))",
]


# for test_string in test_strings:
#     parsedString = parse_struct_inner_type_string(test_string)
#     # parsedString.pprint()
#     dictionary = parsedString.asDict()
#     _flatten_extra_array_wrapping(dictionary)
#     print(dictionary)
#     print('\n')


parsedString = parse_struct_inner_type_string(test_strings[5])
#
print(parsedString)
print('\n')
dictionary = parsedString.asDict()
print(dictionary)
print('\n')
print(decorate_columns_dict('base_column', dictionary, test_strings[5]))
print('\n')
# print(parsedString.originalTextFor())

#
# test = 'col_1 varchar'
# results = column.parseString(test)
# print(results)
