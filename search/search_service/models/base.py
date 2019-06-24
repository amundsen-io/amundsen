from abc import ABCMeta, abstractmethod
from typing import Set


class Base(metaclass=ABCMeta):
    """
    A base class for ES model
    """

    @abstractmethod
    def get_attrs(cls) -> Set:
        # return a set of attributes for the class
        ...
