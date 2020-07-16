# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging

from pyhocon import ConfigTree  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor  # noqa: F401
from databuilder.loader.base_loader import Loader  # noqa: F401
from databuilder.task.base_task import Task  # noqa: F401
from databuilder.transformer.base_transformer import Transformer  # noqa: F401
from databuilder.transformer.base_transformer \
    import NoopTransformer  # noqa: F401
from databuilder.utils.closer import Closer


LOGGER = logging.getLogger(__name__)


class DefaultTask(Task):
    """
    A default task expecting to extract, transform and load.

    """

    # Determines the frequency of the log on task progress
    PROGRESS_REPORT_FREQUENCY = 'progress_report_frequency'

    def __init__(self,
                 extractor,
                 loader,
                 transformer=NoopTransformer()):
        # type: (Extractor, Loader, Transformer) -> None
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

        self._closer = Closer()
        self._closer.register(self.extractor.close)
        self._closer.register(self.transformer.close)
        self._closer.register(self.loader.close)

    def init(self, conf):
        # type: (ConfigTree) -> None
        self._progress_report_frequency = \
            conf.get_int('{}.{}'.format(self.get_scope(), DefaultTask.PROGRESS_REPORT_FREQUENCY), 500)

        self.extractor.init(Scoped.get_scoped_conf(conf, self.extractor.get_scope()))
        self.transformer.init(Scoped.get_scoped_conf(conf, self.transformer.get_scope()))
        self.loader.init(Scoped.get_scoped_conf(conf, self.loader.get_scope()))

    def run(self):
        # type: () -> None
        """
        Runs a task
        :return:
        """
        LOGGER.info('Running a task')
        try:
            record = self.extractor.extract()
            count = 1
            while record:
                record = self.transformer.transform(record)
                if not record:
                    record = self.extractor.extract()
                    continue
                self.loader.load(record)
                record = self.extractor.extract()
                count += 1
                if count > 0 and count % self._progress_report_frequency == 0:
                    LOGGER.info('Extracted {} records so far'.format(count))

        finally:
            self._closer.close()
