from abc import ABCMeta, abstractmethod


class BaseCallerRetriever(metaclass=ABCMeta):

    @abstractmethod
    def get_caller(self) -> str:
        pass
