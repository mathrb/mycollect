"""
    Base for data managers
"""
import abc
from typing import Any


class DataManager(metaclass=abc.ABCMeta):
    """
        Datamanager base class
    """

    @abc.abstractmethod
    def store_raw_data(self, provider: str, data: Any) -> None:
        """
            Store some data
        """

    def read_raw_data(self, provider: str, timestamp: int):
        """
            Read raw data
        """
