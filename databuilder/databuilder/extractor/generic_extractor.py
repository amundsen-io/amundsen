import importlib
from typing import Iterable, Any  # noqa: F401

from pyhocon import ConfigTree  # noqa: F401

from databuilder.extractor.base_extractor import Extractor


class GenericExtractor(Extractor):
    """
    Extractor to extract any arbitrary values from users.
    """
    EXTRACTION_ITEMS = 'extraction_items'

    def init(self, conf):
        # type: (ConfigTree) -> None
        """
        Receives a list of dictionaries which is used for extraction
        :param conf:
        :return:
        """
        self.conf = conf
        self.values = conf.get(GenericExtractor.EXTRACTION_ITEMS)  # type: Iterable[Any]

        model_class = conf.get('model_class', None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)
            results = [self.model_class(**result)
                       for result in self.values]

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
        return 'extractor.generic'
