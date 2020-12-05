"""Aggregators are class that reads a bunch of data and makes sense of it
"""
import abc
from typing import Iterable
from mycollect.structures import MyCollectItem


class Aggregator(metaclass=abc.ABCMeta):  # pylint: disable= R0903

    """Aggregator base class
    """

    def __init__(self, schedule: str = None, notify: str = None, **kwargs):  # pylint: disable=unused-argument
        self._schedule = schedule
        self._notify = notify

    def aggregates(self, items: Iterable[MyCollectItem]) -> dict:
        """Aggregates a list of items

        Args:
            items (Iterable[MyCollectItem]): items to aggregate

        Returns:
            dict: the meaningful representation
        """

    @property
    def schedule(self) -> str:
        """Gets the schedule defined in configuration

        Returns:
            str: schedule
        """
        return self._schedule

    @property
    def notify(self) -> str:
        """Gets the notification channel

        Returns:
            str: notification channel name
        """
        return self._notify
