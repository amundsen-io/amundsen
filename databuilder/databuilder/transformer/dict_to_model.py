# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging

from pyhocon import ConfigTree  # noqa: F401
from typing import Any, Dict  # noqa: F401

from databuilder.transformer.base_transformer import Transformer

MODEL_CLASS = 'model_class'

LOGGER = logging.getLogger(__name__)


class DictToModel(Transformer):
    """
    Transforms dictionary into model
    """

    def init(self, conf):
        # type: (ConfigTree) -> None

        model_class = conf.get_string(MODEL_CLASS)
        module_name, class_name = model_class.rsplit(".", 1)
        mod = importlib.import_module(module_name)
        self._model_class = getattr(mod, class_name)

    def transform(self, record):
        # type: (Dict[str, Any]) -> Dict[str, Any]

        return self._model_class(**record)

    def get_scope(self):
        # type: () -> str
        return 'transformer.dict_to_model'
