"""
    Base for data managers
"""
import abc
from typing import Any, Iterable

from mycollect.structures import MyCollectItem


class Storage(metaclass=abc.ABCMeta):
    """
        Datamanager base class
    """

    @abc.abstractmethod
    def store_item(self, item: MyCollectItem) -> None:
        """
            Store some data
        """

    def fetch_items(self, timestamp: int) -> Iterable[MyCollectItem]:
        """
            Read raw data
        """
