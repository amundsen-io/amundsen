import logging
import six
from pyhocon import ConfigTree  # noqa: F401
from typing import Any  # noqa: F401

from databuilder.transformer.base_transformer import Transformer


LOGGER = logging.getLogger(__name__)


# Config keys
REGEX_REPLACE_TUPLE_LIST = 'regex_replace_tuple_list'
ATTRIBUTE_NAME = 'attribute_name'


class RegexStrReplaceTransformer(Transformer):
    """
    Generic string replacement transformer using REGEX.
    User can pass list of tuples where tuple contains regex and replacement pair.
    """
    def init(self, conf):
        # type: (ConfigTree) -> None
        self._regex_replace_tuples = conf.get_list(REGEX_REPLACE_TUPLE_LIST)
        self._attribute_name = conf.get_string(ATTRIBUTE_NAME)

    def transform(self, record):
        # type: (Any) -> Any
        val = getattr(record, self._attribute_name)
        if six.PY2 and isinstance(val, six.text_type):
            val = val.encode('utf-8', 'ignore')

        for regex_replace_tuple in self._regex_replace_tuples:
            val = val.replace(regex_replace_tuple[0], regex_replace_tuple[1])

        setattr(record, self._attribute_name, val)
        return record

    def get_scope(self):
        # type: () -> str
        return 'transformer.regex_str_replace'
