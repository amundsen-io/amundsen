# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import importlib
import time
from typing import Iterable, Any  # noqa: F401

from pyhocon import ConfigTree  # noqa: F401

from databuilder.extractor.generic_extractor import GenericExtractor


class Neo4jEsLastUpdatedExtractor(GenericExtractor):
    """
    Extractor to extract last updated timestamp for neo4j and Es
    """

    def init(self, conf):
        # type: (ConfigTree) -> None
        """
        Receives a list of dictionaries which is used for extraction
        :param conf:
        :return:
        """
        self.conf = conf

        model_class = conf.get('model_class', None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)
            last_updated_timestamp = int(time.time())
            result = {'timestamp': last_updated_timestamp}
            results = [self.model_class(**result)]
            self._iter = iter(results)
        else:
            raise RuntimeError('model class needs to be provided!')

    def extract(self):
        # type: () -> Any
        """
        Fetch one sql result row, convert to {model_class} if specified before
        returning.
        :return:
        """
        try:
            result = next(self._iter)
            return result
        except StopIteration:
            return None

    def get_scope(self):
        # type: () -> str
        return 'extractor.neo4j_es_last_updated'
