# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, Dict  # noqa: F401

from pyhocon import ConfigTree  # noqa: F401

from databuilder.transformer.base_transformer import Transformer

FIELD_NAMES = 'field_names'  # field name to be removed

LOGGER = logging.getLogger(__name__)


class RemoveFieldTransformer(Transformer):
    """
    Remove field in Dict by specifying list of fields (keys).

    """

    def init(self, conf):
        # type: (ConfigTree) -> None
        self._field_names = conf.get_list(FIELD_NAMES)

    def transform(self, record):
        # type: (Dict[str, Any]) -> Dict[str, Any]

        for k in self._field_names:
            if k in record:
                del record[k]

        return record

    def get_scope(self):
        # type: () -> str
        return 'transformer.remove_field'
