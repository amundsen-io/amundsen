from typing import Dict


def get_query_param(args: Dict, param: str, error_msg: str = None) -> str:
    value = args.get(param)
    if value is None:
        msg = 'A {0} parameter must be provided'.format(param) if error_msg is not None else error_msg
        raise Exception(msg)
    return value
