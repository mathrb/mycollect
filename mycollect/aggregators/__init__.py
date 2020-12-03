"""Aggregators are class that reads a bunch of data and makes sense of it
"""
import abc
from typing import Iterable
from mycollect.structures import MyCollectItem


class Aggregator(metaclass=abc.ABCMeta):  # pylint: disable= R0903

    """Aggregator base class
    """

    def aggregates(self, items: Iterable[MyCollectItem]) -> dict:
        """Aggregates a list of items

        Args:
            items (Iterable[MyCollectItem]): items to aggregate

        Returns:
            dict: the meaningful representation
        """
