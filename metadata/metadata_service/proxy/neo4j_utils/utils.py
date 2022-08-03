from typing import (Any, Dict, Iterable, List, Optional, Tuple,  # noqa: F401
                    Union, no_type_check)

@no_type_check
def safe_get(dct, *keys):
    """
    Helper method for getting value from nested dict. This also works either key does not exist or value is None.
    :param dct:
    :param keys:
    :return:
    """
    for key in keys:
        dct = dct.get(key)
        if dct is None:
            return None
    return dct