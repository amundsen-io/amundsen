# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from pyhocon import ConfigTree  # noqa: F401
from typing import Any, Dict  # noqa: F401

from databuilder.transformer.base_transformer import Transformer

TEMPLATE = 'template'
FIELD_NAME = 'field_name'  # field name to UPSERT

LOGGER = logging.getLogger(__name__)


class TemplateVariableSubstitutionTransformer(Transformer):
    """
    Add/Replace field in Dict by string.format based on given template and provide record Dict as a template parameter
    https://docs.python.org/3.4/library/string.html#string.Formatter.format

    """

    def init(self, conf):
        # type: (ConfigTree) -> None

        self._template = conf.get_string(TEMPLATE)
        self._field_name = conf.get_string(FIELD_NAME)

    def transform(self, record):
        # type: (Dict[str, Any]) -> Dict[str, Any]

        val = self._template.format(**record)
        record[self._field_name] = val
        return record

    def get_scope(self):
        # type: () -> str
        return 'transformer.template_variable_substitution'
