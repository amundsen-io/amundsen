import abc

from pyhocon import ConfigTree  # noqa: F401

from databuilder import Scoped
from databuilder.utils.closer import Closer


class Job(Scoped):
    closer = Closer()

    """
    A Databuilder job that represents single work unit.
    """
    @abc.abstractmethod
    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    @abc.abstractmethod
    def launch(self):
        # type: () -> None
        """
        Launch a job
        :return: None
        """
        pass

    def get_scope(self):
        # type: () -> str
        return 'job'
