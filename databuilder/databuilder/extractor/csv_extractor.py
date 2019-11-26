import csv
import importlib

from pyhocon import ConfigTree  # noqa: F401
from typing import Any, Iterator  # noqa: F401

from databuilder.extractor.base_extractor import Extractor


class CsvExtractor(Extractor):
    # Config keys
    FILE_LOCATION = 'file_location'

    """
    An Extractor that extracts records via CSV.
    """
    def init(self, conf):
        # type: (ConfigTree) -> None
        """
        :param conf:
        """
        self.conf = conf
        self.file_location = conf.get_string(CsvExtractor.FILE_LOCATION)

        model_class = conf.get('model_class', None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)
        self._load_csv()

    def _load_csv(self):
        # type: () -> None
        """
        Create an iterator to execute sql.
        """
        if not hasattr(self, 'results'):
            with open(self.file_location, 'r') as fin:
                self.results = [dict(i) for i in csv.DictReader(fin)]

        if hasattr(self, 'model_class'):
            results = [self.model_class(**result)
                       for result in self.results]
        else:
            results = self.results
        self.iter = iter(results)

    def extract(self):
        # type: () -> Any
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self.iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self):
        # type: () -> str
        return 'extractor.csv'
